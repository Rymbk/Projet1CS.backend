from rest_framework import serializers
from .models import Hotel,Vole


class voleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vole
        fields = [
            'nom',
            'aeroprt',
            'date_depart',
            'heur_depart',
            'date_arrivee',
            'heur_arrivee' ,
            'nb_places',
        ]
        
class hotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            'nom',
            'adress',
        ]
    
