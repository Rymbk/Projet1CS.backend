from django.shortcuts import render
# from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from authentication.models import user
from rest_framework.response import Response
from registration.models import Baladiya, Winners
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from django.http import JsonResponse
from .serializers import hotelSerializer,voleSerializer
from django.shortcuts import get_object_or_404
from .models import Vole,Hotel
from rest_framework.renderers import JSONRenderer


@api_view(["GET"])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def user_list(request):
    role = request.GET.get('role')
    province = request.GET.get('province')
    city = request.GET.get('city')
    query = request.GET.get('query')
    users_list = user.objects.exclude(role='Hedj').exclude(email=request.user.email)
    if query:
        users_list = users_list.filter(email__contains=query)
    if role:
        users_list = users_list.filter(role=role)
    if province and city:
        users_list = users_list.filter(baladiya__id=city) | users_list.filter(province=province).filter(city=Baladiya.objects.get(id=city).name)
    if province and not city:
        users_list = users_list.filter(baladiya__wilaya=province) | users_list.filter(province=province)

    user_ids = users_list.values_list('id', flat=True)
    users_list = []

    user_cities = request.user.baladiya_set
    user_city_ids = user_cities.values_list('id', flat=True)
    manager_user_ids = Baladiya.objects.filter(
        id__in=user_city_ids
    ).filter(
        id_utilisateur__id__in=user_ids
    ).values_list('id_utilisateur__id', flat=True).distinct()

    normal_user_ids = []
    for city in user_cities.all():
        normal_user_ids.extend(user.objects.filter(province=city.wilaya).filter(city=city.name).filter(id__in=user_ids).values_list('id', flat=True))

    users_list = user.objects.filter(id__in=set(list(manager_user_ids) + normal_user_ids))

    paginator = PageNumberPagination()
    paginator.page_size = 5
    users = paginator.paginate_queryset(users_list, request)
    
    serialized_user = [{
        'id': u.id,
        'email': u.email,
        'firstName': u.first_name,
        'lastName' : u.last_name,
        'role': u.role,
        'provinces':u.baladiya_set.values_list('wilaya', flat=True).distinct(),
        'cities': u.baladiya_set.values_list('id', flat=True),
    } for u in users] if users else []
    
    return paginator.get_paginated_response(serialized_user)
 
@api_view(["PATCH"])
@renderer_classes([JSONRenderer])
def role_baladiyet_assignement(request):
    try :
        user_id = request.data.get('id')
        user_role = request.data.get('role')
        chosen_baladiya = request.data.get('cities')
        u = user.objects.get(id=user_id)

        common_resp_users = Baladiya.objects.filter(id__in=chosen_baladiya).filter(id_utilisateur__role=user_role).values('id_utilisateur')
        if len(common_resp_users) > 0:
            return Response({ "message": "responsibility already assigned.", "responsable": user.objects.get(id=common_resp_users[0]['id_utilisateur']).email }, 400)

        u.role = user_role
        u.baladiya_set.set(Baladiya.objects.filter(id__in=chosen_baladiya))
        u.save()

        return Response({'message':'association done'})
    except u.DoesNotExist:
        return Response({'error':'user not found'})

@api_view(["GET"])
@renderer_classes([JSONRenderer])
def winners_list(request):
    winners_list = Winners.objects.all()
    
    data = []
    for winner in winners_list:
        
        winner_data = {
            "nin": winner.nin,
            "paiement":winner.payement,
            "visite_medicale":winner.visite,
            "hedj_info": None,
            "user_info": None
        }
        
        
        
        try:
            user_ = user.objects.get(id=winner.nin)
        except Haaj.DoesNotExist:
            user_ = None

        if user_:
            winner_data['user_info'] = {
                    'last_name': user_.last_name,
                    'first_name': user_.first_name,
                    'email': user_.email
                }
            
            
            try:
                haaj = Haaj.objects.get(user_id=user_.id)
            except Haaj.DoesNotExist:
                haaj = None
             
                
            if haaj and user_.gender == "F":
                
                
                winner_data['hedj_info']={
                    "maahram_id":haaj.maahram_id if haaj.maahram_id else None
                }
                
            
        data.append(winner_data)
    
    return JsonResponse({'users':data})
    
@api_view(["POST"]) 
@renderer_classes([JSONRenderer])      
def add_hotel(request):
    serializer = hotelSerializer(data=request.data) 
    
    if serializer.is_valid():
        serializer.save()
        
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=404) 


@api_view(["POST"])
@renderer_classes([JSONRenderer])
def add_vol(request):
    serializer = voleSerializer(data=request.data)  
    
    if serializer.is_valid():
        serializer.save()
       
        
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=404)            


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def list_hotel(request):
    hotels = Hotel.objects.all()
    serialized_hotels=[]

    
    for h in hotels:
        serialized_hotel = {
            "id": h.id,
            "nom":h.nom,
            "address":h.adress
        }
        serialized_hotels.append(serialized_hotel)
        
    return Response(serialized_hotels)
    
  
@api_view(["GET"])
@renderer_classes([JSONRenderer])
def list_vole(request):
    voles= Vole.objects.all()
    serialized_voles=[]

    
    for v in voles:
        serialized_vole= {
            "id": v.id,
            "nom":v.nom,
            "aeroport":v.aeroprt,
            "heure_depart":v.heur_depart,
            "heure_arrivee":v.heur_arrivee,
            "date_arrivee":v.date_arrivee,
            "date_depart":v.date_depart,
            "nombre_de_places":v.nb_places
        }
        serialized_voles.append(serialized_vole)
        
    return Response(serialized_voles)
    
@api_view(["POST"])
@renderer_classes([JSONRenderer])
def associate_winner_vol_hotel(request):
    winner_id = request.data.get('winner_id')
    vol_id = request.data.get('vol_id')
    hotel_id = request.data.get('hotel_id')

    try:
        winner = get_object_or_404(Winners, nin=winner_id)
    except Exception as e:
        return Response({"message": "Winner not found"}, status=404)
    
    if hotel_id:
        try:
            hotel_ = get_object_or_404(Hotel, id=hotel_id)
            winner.hotel_set.set([hotel_])
        except Exception as e:
            return Response({"message": "Hotel not found"}, status=404)

    if vol_id:
        try:
            vol_ = get_object_or_404(Vole, id=vol_id)
            winner.vole_set.set([vol_])
        except Exception as e:
            return Response({"message": "Vole not found"}, status=404)



    return Response({"message": "association done"})
    
@api_view(["GET"])
@renderer_classes([JSONRenderer])
# @permission_classes([IsAuthenticated])
def winners_hotel_vol(request):
    # TODO uncomment
    # user_baladiyas = request.user.baladiya_set.all()
    user_baladiyas = user.objects.get(id=0).baladiya_set.all()
    winners_list = Winners.objects.filter(
        nin__in=user.objects.filter(
            city__in=user_baladiyas.values_list('name', flat=True)
        ).filter(
            province__in=user_baladiyas.values_list('wilaya', flat=True).distinct()
        ).values_list("id", flat=True)
    ).filter(payement=True).filter(visite=True)
    
    data = []
    for winner in winners_list:
        hotel_list = winner.hotel_set
        flight_list = winner.vole_set
        hotel = hotel_list[0] if hotel_list.count() > 0 else None
        flight = flight_list[0] if flight_list.count() > 0 else None
        winner_user = user.objects.get(id=winner.nin)
        
        winner_data = {
            "id": winner.id,
            "email": winner_user.email,
            "firstName": winner_user.first_name,
            "lastName": winner_user.last_name,
            "flight": {
                "id": flight.id,
                "name": flight.nom
            } if flight != None else None,
            "hotel": {
                "id": hotel.id,
                "name": hotel.nom
            } if hotel != None else None,
        }
            
        data.append(winner_data)
    
    return Response(data)


