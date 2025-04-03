from rest_framework import serializers
from .models import user


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = [
            'email',
            'password',
            'is_email_verified',
            'first_name',
            'last_name',
            'phone',
            'dateOfBirth',
            'province',
            'city',
            'gender',
            'nombreInscription',
            'role',
            'winner',
            'winning_date',
            'personal_picture'
        ]

        extra_kwargs = { 'password': { 'write_only': True } }
