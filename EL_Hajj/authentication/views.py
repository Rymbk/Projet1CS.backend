from random import randint, random
from django.core.mail import send_mail
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import make_password
from authentication.serializers import userSerializer
from .models import PasswordReset, user
from rest_framework import status
from django.shortcuts import get_object_or_404,render
from registration.models import Baladiya, Haaj, Winners
from rest_framework.decorators import api_view, parser_classes, renderer_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.core.serializers import serialize
from django.contrib.auth import logout, login ,get_user_model,authenticate
from django.urls import reverse 
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated


def get_user_status(u: user):
    if u.role != "Hedj":
        return None
    haaj = None
    try:
        haaj = Haaj.objects.get(user=u)
    except Haaj.DoesNotExist:
        haaj = None

    winner = None
    try:
        winner = Winners.objects.get(nin=u.id)
    except Winners.DoesNotExist:
        winner = None

    registered = haaj != None
    drawing = u.role == "Hedj" and winner != None
    appointment = drawing and winner != None and winner.visite
    payment = appointment and winner != None and winner.payement
    booking = payment and winner != None and winner.hotel_set.count() > 0 and winner.vole_set.count() > 0

    return {
        'registration': registered if registered else None if drawing else False,
        'drawing': drawing,
        'appointment': appointment,
        'payment': payment,
        'booking': booking,
        'done': booking,
    }



@api_view(["POST"])
@parser_classes([JSONParser])
def send_verification_email(request):
    email = request.data["email"]
    # email attached to account
    try:
        user_: user = user.objects.get(email=email)
    except:
        return Response(JSONRenderer().render({ "message": "invalid address" }), 400)

    code = randint(0, 9999)
    try:
        send_mail(
            "Email de confirmation",
            f"Bienvenue sur le site Web El Hajj,\n votre code de confirmation est {code}",
            "celeq.elhajj@gmail.com",
            [email]
        )
        user_.code = f"{code}"
        user_.save()
        return Response(JSONRenderer().render({ "message": "email sent" }), 200)
    except:
        return Response(JSONRenderer().render({ "message": "invalid address" }), 400)

@api_view(["POST"])
@parser_classes([JSONParser])
def verify_email(request):
    email = request.data["email"]
    code = request.data["code"]
    
    user = get_user_model()
    
    try:
        user = user.objects.get(email=email,code=code)
    except user.DoesNotExist:
        return Response(JSONRenderer().render({ "message": "invalid address or code" }), 400)
    user.is_email_verified = True 
    user.save()
    return Response(JSONRenderer().render({ "message": "Email verified" }), 200)
    
@csrf_exempt    
@api_view(['GET', 'POST'])
def register(request):
    data = request.data
    # email = data.get('email')
    # password = data.get('password')
    # first_name = data.get('first_name')
    # last_name = data.get('last_name')
    # phone = data.get('phone')
    # dateOfBirth = data.get('dateOfBirth')
    # city = data.get('city')
    # province = data.get('province')
    # gender = data.get('gender')
    
    
    # hashed_password = make_password(password)
    
    # CHANGE: only use serializer.save
    role = request.data.get("role","user")
    request.data["role"] = role
    request.data["password"] = make_password(request.data["password"])
    serializer = userSerializer(data=request.data)
    # u = user.objects.create(
    #     email = email,
    #     password = hashed_password,
    #     first_name = first_name,
    #     last_name = last_name,
    #     phone = phone,
    #     dateOfBirth = dateOfBirth,
    #     city = city,
    #     province = province,
    #     gender = gender,
    # )
    if serializer.is_valid():
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=404)



@api_view(["POST"])
@parser_classes([JSONParser])
def send_reset_password_email(request):
    email = request.data["email"]
    try:
        user_: user = user.objects.get(email=email)
    except:
        return Response(JSONRenderer().render({ "message": "invalid address" }), 400)

    reset = PasswordReset()
    reset.save()
    reset.usere = user_
    reset.save()
    try:
        hello = ""
    except:
        return Response(JSONRenderer().render({ "message": "failed to send email" }), 400)
    id = reset._get_pk_val()
    link = f"http://localhost:3000/reset-password?id={id}&email={email}"
    try:
        send_mail(
            "Email de confirmation",
            f"Votre demande de réinitialisation de mot de passe a été approuvée. Veuillez suivre le lien\n {link}\n pour réinitialiser votre mot de passe.",
            "celeq.elhajj@gmail.com",
            [email]
        )
        return Response(JSONRenderer().render({ "message": "email sent" }), 200)
    except:
        return Response(JSONRenderer().render({ "message": "invalid address" }), 400)

@api_view(["PATCH"])
@parser_classes([JSONParser])
def reset_password(request):
    email = request.data["email"]
    reset_id = int(request.data["id"])
    new_password = request.data["newPassword"]
    reset: PasswordReset = PasswordReset.objects.get(pk=reset_id)
    user_: user = user.objects.get(email=email)
    try:
        if user_._get_pk_val() != reset.usere.id:
            return Response(JSONRenderer().render({ "message": "invalid token" }), 400)
        if user_.check_password(new_password):
            return Response(JSONRenderer().render({ "message": "duplicate password" }), 409)
        user_.set_password(new_password)
        user_.save()
        reset.delete()
        return Response(JSONRenderer().render({ "message": "reset successful" }), 200)
    except:
        return Response(JSONRenderer().render({ "message": "failed to reset password" }), 400)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@csrf_exempt
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    remember = request.data.get("remember")

    if email and password:
        u= authenticate(request, username=email, password=password)

        if u is not None:
            # CHANGE: no verification of email on login
            login(request,u)
            if remember:
                request.session.set_expiry(0)
            resp = userSerializer(u).data
            resp["id"] = u.id
            resp["personal_picture"] = u.personal_picture.url if u.personal_picture != None else None            
            resp["status"] = get_user_status(u)
                
            return Response(resp,status=200)
            
        else:
            return Response({'error': 'Invalid email or password'}, status=401)
    else:
        return Response({'error': 'Email and password are required'}, status=400)
    

def convert_to_serializable(data):
    """
    Recursively convert non-serializable objects to serializable types.
    """
    if isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, user):
        # Convert CustomUser object to a dictionary of serializable fields
        return {
            'id': data.id,
            'email': data.email,
            # Include other serializable fields of CustomUser
        }
    # Add more conversions as needed
    else:
        # Return the data as is for other types
        return data


   
@csrf_exempt 
def get_user_info(request,email): 
    if request.method == 'GET':
            try:
                user_ = get_object_or_404(user,email=email)
                baladiyas = Baladiya.objects.filter(id_utilisateur=user_.id)
                print(baladiyas)
                bala =[]
                for baladiya in baladiyas :
                    bala.append(baladiya.id)
                
                print(baladiya)
                
                user_info = {
                    'first_name' : user_.first_name,
            'last_name' : user_.last_name,
            'phone' : user_.phone,
            "city" :user_.city,
            'province' : user_.province,
            'gender' : user_.gender,
            'email' : user_.email,
            'dateOfBirth' : user_.dateOfBirth,
            'role' : user_.role,
            'is_email_verified' : user_.is_email_verified
                }
                user_info = convert_to_serializable(user_info)
                
                return JsonResponse(user_info,content_type = 'application/json')
            
            except user.DoesNotExist:
                return JsonResponse({'error':'user not found'},status=404)
            
    else : 
        return JsonResponse({'error':'methode not allowed'},status=405)


@api_view(["PATCH"])       
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user_instance = request.user
    if len(request.FILES) > 0:
        user_instance.personal_picture = request.FILES["image"]
    serializer = userSerializer(user_instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        url = user_instance.personal_picture.metadata["secure_url"] if user_instance.personal_picture != None else None
        response = serializer.data
        response["personal_picture"] = url
        return Response(response)
    return Response({ "errors": serializer.errors }, 400)

        
    
@api_view(["GET"])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def get_currently_logged_user(request):
    if request.user.is_authenticated :
        current_user = request.user
        haaj = None
        try:
            haaj = Haaj.objects.get(user=current_user)
        except Haaj.DoesNotExist:
            haaj = None

        winner = None
        try:
            winner = Winners.objects.get(nin=current_user.id)
        except Winners.DoesNotExist:
            winner = None

        user_info = {
            'id': current_user.id,
            'first_name' : current_user.first_name,
            'last_name' : current_user.last_name,
            'phone' : current_user.phone,
            "city" :current_user.city,
            'province' : current_user.province,
            'gender' : current_user.gender,
            'email' : current_user.email,
            'dateOfBirth' : current_user.dateOfBirth,
            'role' : current_user.role,
            'is_email_verified' : current_user.is_email_verified,
            'personal_picture': current_user.personal_picture.url if current_user.personal_picture != None else None,
            'status': get_user_status(current_user),
        }
        return Response(user_info, status=200)

    else : 
        return Response({"error":"not authenticated"}, status=400)
    
@api_view(["POST"])
def logout_user(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"})


@api_view(['GET'])
@parser_classes([JSONParser])
def default(request):
    try:
        send_mail(
            "Welcome",
            "How are you doing",
            "celeq.elhajj@gmail.com",
            ["marzoukayouness@gmail.com"]
        )
        return Response(JSONRenderer().render({ "message": "email sent successfully" }))
    except:
        return Response(JSONRenderer().render({ "message": "failed to send email" }), 400)

@api_view(["PATCH"])
def image_upload(request):
    user_instance = user.objects.get(email="ya.merzouka@esi-sba.dz")
    user_instance.personal_picture = request.FILES["image"]
    user_instance.save()
    print(user_instance.personal_picture.__dict__)
    return Response({ "url": f"{user_instance.personal_picture.metadata['secure_url']}" })
    
