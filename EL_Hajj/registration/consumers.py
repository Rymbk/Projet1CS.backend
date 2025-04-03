import json
import random
from channels.generic.websocket import WebsocketConsumer
from .models import Haaj, Winners, Baladiya, Tirage
from authentication.models import user


class TirageConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def fetch_winner(self, id_utilisateur):
        user = user.objects.get(id=id_utilisateur)
        baladiyas_in_group = Baladiya.objects.filter(id_utilisateur=user)
        baladiya_names = [baladiya.name for baladiya in baladiyas_in_group]
        first_baladiya = Baladiya.objects.filter(id_utilisateur=id_utilisateur).first()

        condidats = []

        for baladiya_name in baladiya_names:
            haajs_in_city = Haaj.objects.filter(user__city=baladiya_name)
            
            condidats.extend(haajs_in_city)
            

        id_tirage = first_baladiya.tirage.id
        number_of_winners_needed = Tirage.objects.get(id=id_tirage).nombre_de_place
        type_de_tirage = Tirage.objects.get(id=id_tirage).type_tirage

        selected_winners = []

        if type_de_tirage == 1:
            while len(selected_winners) < number_of_winners_needed:
                selected_condidat = random.choice(condidats)
                if selected_condidat.user.gender == 'M':
                    selected_winners.append(selected_condidat.user)
                    condidats.remove(selected_condidat)
                    Winners.objects.create(nin=selected_condidat.user.id)
                    
                elif selected_condidat.user.gender == 'F':
                    selected_winners.append(selected_condidat.user)
                    condidats.remove(selected_condidat)
                    Winners.objects.create(nin=selected_condidat.user.id)
                    maahram_instance = user.objects.get(id=selected_condidat.maahram_id)
                    selected_winners.append(maahram_instance)
                    Winners.objects.create(nin=maahram_instance.id)
                    
        return selected_winners

    def receive(self, text_data):
        message = json.loads(text_data)
        if message.get('action') == 'melange':
            id_utilisateur = int(message.get('id_utilisateur'))
            self.fetch_winner(id_utilisateur)
