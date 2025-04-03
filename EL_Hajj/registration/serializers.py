from rest_framework import serializers
from .models import Haaj, Tirage, Baladiya, Winners
from django.utils import timezone
from authentication.models import user


class HaajSerializer(serializers.ModelSerializer):
    class Meta:
        model = Haaj
        fields = '__all__'
        read_only_fields = ['user']  

    def create(self, validated_data):
        request = self.context.get('request')
        utilisateur_instance = request.user
        validated_data['user'] = utilisateur_instance  
        return Haaj.objects.create(**validated_data)
        
    def validate_card_expiration_date(self, value):
        current_date = timezone.now().date()
        if value < current_date  + timezone.timedelta(days=180):  
            raise serializers.ValidationError("The card expiration date must be at least six months in the future.")
        return value

    def validate_passport_expiration_date(self, value):
        current_date = timezone.now().date()
        if value < current_date + timezone.timedelta(days=180):
            raise serializers.ValidationError("The passport expiration date must be at least six months in the future.")
        return value
    

    

        
        
        
    
class BaladiyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baladiya
        fields = ['name', 'id_utilisateur', 'tirage'] 


class TirageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tirage
        fields = '__all__'
 
        
class WinnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winners
        fields = '__all__'
       
        
