from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from authentication.serializers import userSerializer
from .serializers import HaajSerializer 
from authentication.models import user 
from rest_framework.permissions import IsAuthenticated
from .models import  Baladiya, Tirage, Haaj, Winners,WaitingList
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.decorators import api_view, parser_classes, renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.shortcuts import render
import random 
from django.utils import timezone
from registration.serializers import WinnersSerializer

from django.core.exceptions import ObjectDoesNotExist

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def registration(request):
    authenticated_user = request.user  
    if request.method == 'GET':
        utilisateur_data = {
            'emailUtilisateur': authenticated_user.email,
            'first_name': authenticated_user.first_name,
            'last_name': authenticated_user.last_name,
            'dateOfBirth': authenticated_user.dateOfBirth,
            'city' : authenticated_user.city,
            'gender' : authenticated_user.gender
        }
        return JsonResponse(utilisateur_data)

    elif request.method == 'POST':
        if authenticated_user.winner:
            last_winning_date = authenticated_user.winning_date
            ten_years_ago = datetime.now() - timedelta(days=365 * 10)
            if last_winning_date > ten_years_ago:
                return Response("You cannot register for the draw as you have won in the last 10 years.", status=status.HTTP_400_BAD_REQUEST)
        
        serializer_data = request.data.copy() 
        haaj_serializer = HaajSerializer(data=serializer_data, context={'request': request})
        if haaj_serializer.is_valid():
            authenticated_user.nombreInscription += 1
            authenticated_user.role = "Hedj"
            authenticated_user.save()
            return Response("Success", status=status.HTTP_201_CREATED)
        return Response(haaj_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    






@api_view(['GET'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def baladiya_names_by_utilisateur(request):
    try:
        utilisateur_obj = request.user
        baladiya_names = utilisateur_obj.baladiya_set.values_list('name', flat=True)
        return Response({'baladiya_names': list(baladiya_names)}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)





@api_view(['POST'])
@parser_classes([JSONParser])
@parser_classes([IsAuthenticated])
def associate_tirage_with_baladiyas(request):
    type_tirage = request.data.get('type_tirage')
    nombre_de_place = request.data.get('nombre_de_place')
    tranche_age = request.data.get('tranche_age')
    
    utilisateur_obj = request.user

    
    baladiya_ids = utilisateur_obj.baladiya_set.values_list('id', flat=True)

    
    tirage = Tirage.objects.create(
        type_tirage=type_tirage,
        nombre_de_place=nombre_de_place,
        tranche_age=tranche_age,
    )

    
    for baladiya_id in baladiya_ids:
        baladiya = get_object_or_404(Baladiya, id=baladiya_id)
        baladiya.tirage = tirage
        baladiya.save()

 
    return Response({'message': 'Tirage information associated with Baladiyas successfully'}, status=201)


def get_male_winner_info(winner: user):
    return {
        'id':winner.id,
        'city': winner.city,
        'first_name': winner.first_name,
        'last_name': winner.last_name,
        'personal_picture': winner.personal_picture.url if winner.personal_picture else None,
        'gender': winner.gender
    }

def get_female_winner_info(winner: user, mahram: user):
    return {
        'id':winner.id,
        'city': winner.city,
        'first_name': winner.first_name,
        'last_name': winner.last_name,
        'personal_picture': winner.personal_picture.url if winner.personal_picture else None,
        'gender': winner.gender,
        'maahram_id': mahram.id
    }


def save_male_winner(selected: Haaj, candidats: list[Haaj], selected_winners):
    selected.user.winner = True 
    selected.user.nombreInscription = 0
    selected.user.winning_date= timezone.now()  
    selected.save()
    selected_user = selected.user
    selected_winners.append(get_male_winner_info(selected_user))
    Winners.objects.create(nin=selected.user.id)
    candidats = list(filter(lambda candidat: candidat.id != selected.id, candidats))
    return [candidats, selected_winners]

def save_female_winner(selected: Haaj, candidats: list[Haaj], selected_winners):
    selected.user.winner = True 
    selected.user.nombreInscription = 0
    selected.user.winning_date= timezone.now()  
    selected.user.save()
    Winners.objects.create(nin=selected.user.id)
    candidats = list(filter(lambda candidat: candidat.id != selected.id, candidats))

    maahram_instance = user.objects.get(id=selected.maahram_id)
    selected_user = selected.user
    selected_winners.append(get_female_winner_info(selected_user, maahram_instance))
    if maahram_instance.id not in list(map(lambda winner: winner["id"], selected_winners)):
        maahram_instance.winner = True 
        maahram_instance.nombreInscription = 0
        maahram_instance.role = 'Hedj'
        maahram_instance.winning_date= timezone.now()
        maahram_instance.save()
        selected_winners.append(get_male_winner_info(maahram_instance))
        Winners.objects.create(nin=maahram_instance.id)
        candidats = list(filter(lambda candidat: candidat.user.id != maahram_instance.id, candidats))
    return [candidats, selected_winners, maahram_instance]

def save_male_waiting(selected: Haaj, candidats: list[Haaj], selected_waiting):
    selected_user = selected.user
    selected_waiting.append(get_male_winner_info(selected_user))
    candidats = list(filter(lambda candidat: candidat.id != selected.id, candidats))
    WaitingList.objects.create(nin=selected.user.id)
    return [candidats, selected_waiting]


def save_female_waiting(selected: Haaj, candidats: list[Haaj], selected_waiting):
    candidats = list(filter(lambda candidat: candidat.id != selected.id, candidats))
    WaitingList.objects.create(nin=selected.user.id)
    maahram_instance = user.objects.get(id=selected.maahram_id)
    selected_user = selected.user
    selected_waiting.append(get_female_winner_info(selected_user, maahram_instance))
    if maahram_instance.id not in list(map(lambda waiting: waiting["id"], selected_waiting)):
        selected_waiting.append(get_male_winner_info(maahram_instance))
        WaitingList.objects.create(nin=maahram_instance.id)
        candidats = list(filter(lambda candidat: candidat.user.id != maahram_instance.id, candidats))
    return [candidats, selected_waiting, maahram_instance]

def get_allots(allotted, real):
    extra = 0
    for i in range(len(allotted)):
        if real[i] < allotted[i]:
            extra += allotted[i] - real[i]
            allotted[i] = real[i]
    
    # distribution of extra allots
    prev = 0
    while prev != extra and extra > 0:
        prev = extra
        for i in range(len(allotted)):
            if allotted[i] < real[i]:
                allotted[i] += 1
                extra -= 1
            if extra == 0:
                break
    return allotted

@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def fetch_winners(request):
    user_instance = request.user
    role_user=user_instance.role
    baladiya_group = []
    if role_user == 'responsable tirage':
        baladiya_group = Baladiya.objects.filter(id_utilisateur=user_instance)
        first_baladiya = baladiya_group[0]
    else:
        user_city=user_instance.city
        wilaya_city=user_instance.province
        first_baladiya=Baladiya.objects.get(name=user_city, wilaya=wilaya_city)
        tirage_baladiya=first_baladiya.tirage_id
        baladiya_group = Baladiya.objects.filter(tirage_id=tirage_baladiya)

    if first_baladiya and first_baladiya.tirage and first_baladiya.tirage.tirage_fini:
        winner_user_ids = []
        for baladiya in baladiya_group:
            winner_user_ids.extend(
                Winners.objects
                .filter(nin__in=user.objects.filter(city__iexact=baladiya.name)
                .filter(province=baladiya.wilaya).values_list('id', flat=True))
                .order_by('id')
                .values_list('nin', flat=True)
            )
        selected_winners = []
        user_ids = []
        for winner_id in winner_user_ids:
            winner = user.objects.get(id=winner_id)
            if winner.id not in user_ids:
                if winner.gender == 'M':
                    selected_winners.append(get_male_winner_info(winner))
                else:
                    mahram = user.objects.get(id=Haaj.objects.get(user=winner).maahram_id)
                    winner_json = get_female_winner_info(winner, mahram) 
                    selected_winners.append(winner_json)
                    user_ids.append(winner.id)
                    if mahram.id not in user_ids:
                        mahram_json = {
                            'id':mahram.id,
                            'city': winner.city,
                            'first_name': mahram.first_name,
                            'last_name': mahram.last_name,
                            'personal_picture': mahram.personal_picture.url if mahram.personal_picture else None,
                            'gender': mahram.gender
                        }
                        user_ids.append(mahram.id)
                        selected_winners.append(mahram_json)
        return Response({ "winners": selected_winners, 'nombre_de_place': first_baladiya.tirage.nombre_de_place }, 200)

    else:       
        condidats = []
        for baladiya in baladiya_group:
            haajs_in_city = Haaj.objects.filter(user__city=baladiya.name).filter(user__province=baladiya.wilaya)
            condidats.extend(haajs_in_city)
        condidats2 =[]

        for haaj in condidats:
            times_to_add = haaj.user.nombreInscription
            condidats2.extend([haaj] * times_to_add)


        id_tirage = first_baladiya.tirage.id
        tirage = Tirage.objects.get(id=id_tirage)
        number_of_winners_needed = tirage.nombre_de_place
        number_of_waiting_needed = tirage.nombre_waiting
        type_de_tirage = tirage.type_tirage
        tirage.tirage_fini = True
        tirage.save()

        
        selected_winners = []
        selected_waiting=[]

        if type_de_tirage == 1:
            while len(selected_winners) < number_of_winners_needed and len(condidats2) > 0:
                selected_condidat = random.choice(condidats2)
                if selected_condidat.user.gender == 'M':
                    condidats2, selected_winners = save_male_winner(selected_condidat, condidats2, selected_winners)
                elif selected_condidat.user.gender == 'F':
                    if len(selected_winners) == number_of_winners_needed - 1:
                        left_males = [condidat for condidat in condidats2 if condidat.user.gender == 'M']
                        if len(left_males) > 0:
                            last_male_condidat = random.choice(left_males)
                            condidats2, selected_winners = save_male_winner(last_male_condidat, condidats2, selected_winners)

                    else:
                        condidats2, selected_winners, _ = save_female_winner(selected_condidat, condidats2, selected_winners)


            #witing list code................
            while len(selected_waiting) < number_of_waiting_needed and len(condidats2) > 0:
                selected_condidat = random.choice(condidats2)
                if selected_condidat.user.gender == 'M':
                    condidats2, selected_waiting = save_male_waiting(selected_condidat, condidats2, selected_waiting)
                elif selected_condidat.user.gender == 'F':
                    if len(selected_waiting) == number_of_waiting_needed - 1:
                        left_males = [condidat for condidat in condidats2 if condidat.user.gender == 'M']
                        if len(left_males) > 0:
                            last_male_condidat = random.choice(left_males)
                            condidats2, selected_waiting = save_male_waiting(last_male_condidat, condidats2, selected_waiting)
                    else:
                        condidats2, selected_waiting, _ = save_female_waiting(selected_condidat, condidats2, selected_waiting)

                                

        elif type_de_tirage == 2:
            condidats2_over_60 = []
            condidats2_under_60 = []

            for haaj in condidats2:
                user_age_days = (datetime.date.today() - haaj.user.dateOfBirth).days
                user_age_years = user_age_days / 365.2425 
                if user_age_years > 60:
                    condidats2_over_60.append(haaj)
                else:
                    condidats2_under_60.append(haaj)

            selected_winners_old = []
            selected_winners_young = []
            selected_waiting_old=[]
            selected_waiting_young=[]
            tranche_age = Tirage.objects.get(id=id_tirage).tranche_age
            calculated_old = int((tranche_age * number_of_winners_needed) / 100)
            calculated_young = number_of_winners_needed-calculated_old
            nombre_old, nombre_young = get_allots(
                [calculated_old, calculated_young],
                [len(condidats2_over_60), len(condidats2_under_60)]
            )


            if condidats2_over_60:
                while len(selected_winners_old) < nombre_old and len(condidats2_over_60) > 0:
                    selected_condidat = random.choice(condidats2_over_60)
                    if selected_condidat.user.gender == 'M':
                        condidats2_over_60, selected_winners_old = save_male_winner(
                            selected_condidat,
                            condidats2_over_60,
                            selected_winners_old
                        )
                        
                    elif selected_condidat.user.gender == 'F':
                        if len(selected_winners_old) == nombre_old - 1:
                            left_males = [condidat for condidat in condidats2_over_60 if condidat.user.gender == 'M']
                            if len(left_males) > 0:
                                last_male_condidat = random.choice(left_males)
                                condidats2_over_60, selected_winners_old = save_male_winner(
                                    last_male_condidat,
                                    condidats2_over_60,
                                    selected_winners_old
                                )
                        else:
                            condidats2_over_60, selected_winners_old, mahram = save_female_winner(
                                selected_condidat,
                                condidats2_over_60,
                                selected_winners_old
                            )
                            condidats2_under_60 = list(filter(lambda candidat: candidat.user.id != mahram.id, condidats2_under_60))

            if condidats2_under_60:                           
                while len(selected_winners_young) < nombre_young and len(condidats2_under_60) > 0:
                    selected_condidat = random.choice(condidats2_under_60)
                    if selected_condidat.user.gender == 'M':
                        condidats2_under_60, selected_winners_young = save_male_winner(
                            selected_condidat,
                            condidats2_under_60,
                            selected_winners_young
                        )
                        
                    elif selected_condidat.user.gender == 'F':
                        if len(selected_winners_young) == nombre_young - 1:
                            left_males = [condidat for condidat in condidats2_over_60 if condidat.user.gender == 'M']
                            if len(left_males) > 0:
                                last_male_condidat = random.choice(left_males)
                                condidats2_under_60, selected_winners_young, mahram = save_male_winner(
                                    selected_condidat,
                                    condidats2_under_60,
                                    selected_winners_young
                                )
                        else:
                            condidats2_under_60, selected_winners_young, mahram = save_female_winner(
                                selected_condidat,
                                condidats2_under_60,
                                selected_winners_young
                            )
                            condidats2_over_60 = list(filter(lambda candidat: candidat.user.id != mahram.id, condidats2_over_60))





            #tirage  de waiting list........................;
            calculated_old = int((tranche_age * number_of_waiting_needed) / 100)
            calculated_young = number_of_winners_needed-calculated_old
            nombre_old1, nombre_young1 = get_allots(
                [calculated_old, calculated_young],
                [len(condidats2_over_60), len(condidats2_under_60)]
            )

            if condidats2_over_60:
                while len(selected_waiting_old) < nombre_old1 and len(condidats2_over_60) > 0:
                    selected_condidat = random.choice(condidats2_over_60)
                    if selected_condidat.user.gender == 'M':
                        condidats2_over_60, selected_waiting_old = save_male_waiting(
                            selected_condidat,
                            condidats2_over_60,
                            selected_waiting_old
                        )
                        
                    elif selected_condidat.user.gender == 'F':
                        if len(selected_waiting_old) == nombre_old1 - 1:
                            left_males = [condidat for condidat in condidats2_over_60 if condidat.user.gender == 'M']
                            if len(left_males) > 0:
                                last_male_condidat = random.choice(left_males)
                                condidats2_over_60, selected_waiting_old = save_male_waiting(
                                    last_male_condidat,
                                    condidats2_over_60,
                                    selected_waiting_old
                                )
                        else:
                            condidats2_over_60, selected_waiting_old, mahram = save_female_waiting(
                                selected_condidat,
                                condidats2_over_60,
                                selected_waiting_old
                            )
                            condidats2_under_60 = list(filter(lambda candidat: candidat.user.id != mahram.id, condidats2_under_60))


            if condidats2_under_60:                           
                while len(selected_waiting_young) < nombre_young1 and len(condidats2_under_60) > 0:
                    selected_condidat = random.choice(condidats2_under_60)
                    if selected_condidat.user.gender == 'M':
                        condidats2_under_60, selected_waiting_young = save_male_waiting(
                            selected_condidat,
                            condidats2_under_60,
                            selected_waiting_young
                        )
                        
                    elif selected_condidat.user.gender == 'F':
                        if len(selected_waiting_young) == nombre_young1 - 1:
                            left_males = [condidat for condidat in condidats2_under_60 if condidat.user.gender == 'M']
                            if len(left_males) > 0:
                                last_male_condidat = random.choice(left_males)
                                condidats2_under_60, selected_waiting_young = save_male_waiting(
                                    last_male_condidat,
                                    condidats2_under_60,
                                    selected_waiting_young
                                )
                        else:
                            condidats2_under_60, selected_waiting_young, mahram = save_female_waiting(
                                selected_condidat,
                                condidats2_under_60,
                                selected_waiting_young
                            )
                            condidats2_over_60 = list(filter(lambda candidat: candidat.user.id != mahram.id, condidats2_over_60))

        if type_de_tirage == 1:
            selected_winners = selected_winners
            selected_waiting = selected_waiting
        else:
            selected_winners = selected_winners_old + selected_winners_young
            selected_waiting = selected_waiting_old + selected_waiting_young

        return Response({'winners': selected_winners, 'nombre_de_place': number_of_winners_needed}, status=200)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def participants_tirage(request):
    user_instance = request.user
    baladiyat_in_tirage = []
    if user_instance.role == 'responsable tirage':
        baladiyat_in_tirage = Baladiya.objects.filter(id_utilisateur=user_instance)
    else:
        baladiya_instance = get_object_or_404(Baladiya, name=user_instance.city, wilaya=user_instance.province)
        baladiya_tirage_id = baladiya_instance.tirage_id
        baladiyat_in_tirage = Baladiya.objects.filter(tirage_id=baladiya_tirage_id)
    serialized_data = []

    for baladiya in baladiyat_in_tirage:
        haajs_in_city = Haaj.objects.filter(user__city__iexact=baladiya.name).filter(user__province=baladiya.wilaya)
        for haaj in haajs_in_city:
            for _ in range(haaj.user.nombreInscription):
                haaj_data = {
                    'city': haaj.user.city,
                    'first_name': haaj.user.first_name,
                    'last_name': haaj.user.last_name,
                    'personal_picture': haaj.user.personal_picture.url if haaj.user.personal_picture else None,
                }
                serialized_data.append(haaj_data)

    return Response(serialized_data, status=200)
    # try:
    # 
    # except Exception as e:
    #     return Response({'error': str(e)}, status=500) 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_tirage_definition(request):
    try:
        user_instance = user(id=request.user.id)
        baladiya_ids = user_instance.baladiya_set.values_list('id', flat=True)

        if len(baladiya_ids) == 0:
            return JsonResponse({'tirage_definit': False}, status=200)

        for baladiya_id in baladiya_ids:
            baladiya = get_object_or_404(Baladiya, id=baladiya_id)
            if not baladiya.tirage_id:
                return JsonResponse({'tirage_definit': False}, status=200)

        
        return JsonResponse({'tirage_definit': True}, status=200)

    except Exception as e:
          return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def tirage_défini(request):
    try:
        baladiyat = Baladiya.objects.filter(id_utilisateur=request.user.id).first()
        if baladiyat and baladiyat.tirage:
            tirage = baladiyat.tirage
            tirage_data = {
                'type_tirage': tirage.type_tirage,
                'nombre_de_place': tirage.nombre_de_place,
                'tranche_age': tirage.tranche_age,
                'nombre_waiting': tirage.nombre_waiting,
                'tirage_fini': tirage.tirage_fini
            }
            return Response(tirage_data)

        else:
            return Response({'message': 'tirage non défini'}, 404)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
   

#for visite medical...........................................
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def winners_by_baladiya(request):
    try:
        user_instance = request.user

        baladiyas_in_group = Baladiya.objects.filter(id_utilisateur=user_instance)
        baladiya_names = [baladiya.name for baladiya in baladiyas_in_group]

        user_ids_in_city = user.objects.filter(city__in=baladiya_names).values_list('id', flat=True)
        winners = Winners.objects.filter(nin__in=user_ids_in_city)

        winners_data = []
        for winner in winners:
            winner_user = get_object_or_404(user, id=winner.nin)
            user_data = {
                'id_winner': winner.id,
                'first_name': winner_user.first_name,
                'last_name': winner_user.last_name,
                'personal_picture': winner_user.personal_picture.url if winner_user.personal_picture else None,
                'status': winner.visite,
            }
            winners_data.append(user_data)

        return Response({ 'winners': winners_data }, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)



@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def view_tirage(request):
    try:
        
        user_instance = request.user

        
        user_instance.view_tirage = True

        
        user_instance.save()

        return Response({'status': 'success', 'message': 'Vous avez consulté le tirage'}, status=200)
    
    except ObjectDoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH'])
@renderer_classes([JSONRenderer])
def visite_status(request):

    try:

        id_winner = request.data.get('id_winner')
        status = request.data.get('status')
            
        if not id_winner:
            return Response({'error': 'id_winner is required'}, status=400)
            
        try:
            winner = Winners.objects.get(id=id_winner)
        except Winners.DoesNotExist:
            return Response({'error': 'Winner with the provided ID does not exist'}, status=404)
            
        winner.visite = status
        winner.save()
        return Response({'message': 'Winner visit status updated successfully'}, status=200)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
   
    
#for payment.....................
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def winners_accepted(request):
    try:
        
        user_instance = request.user
        
        
        baladiyas_in_group = Baladiya.objects.filter(id_utilisateur=user_instance)
        
        
        baladiya_names = [baladiya.name for baladiya in baladiyas_in_group]
        

        
        winners = Winners.objects.filter(
            nin__in=user.objects.filter(city__in=baladiya_names).values('id'),
            visite=True
        )
        
        
        winners_data = []
        for winner in winners:
            winner_user = get_object_or_404(user, id=winner.nin)
            user_data = {
                'id_winner': winner.id,
                'first_name': winner_user.first_name,
                'last_name': winner_user.last_name,
                'personal_picture': winner_user.personal_picture.url if winner_user.personal_picture else None,
                'status': winner.payement,
            }
            winners_data.append(user_data)
        
        return Response({ 'winners': winners_data }, status=200)
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH'])
@renderer_classes([JSONRenderer])
def payment_status(request):
    try:

        id_winner = request.data.get('id_winner')
        status = request.data.get('status')
        if not id_winner:
            return Response({'error': 'id_winner is required'}, status=400)

        winner = get_object_or_404(Winners, id=id_winner)

        winner.payement = status
        winner.save()
        return Response({'message': 'Winner payment status updated successfully'}, status=200)

    except Exception as e:

        return Response({'error': str(e)}, status=500)

