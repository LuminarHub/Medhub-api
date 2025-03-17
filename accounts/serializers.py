from typing import Any, Dict
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['id'] = user.id
        token['name'] = user.name
        token['email'] = user.email
        token['phone'] = user.phone
        token['image'] = user.image.url if user.image else None
        token['dob'] = user.dob.url if user.dob else None
        token['gender'] = user.gender.url if user.gender else None
        

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['id'] = user.id
        data['name'] = user.name
        data['email'] = user.email
        data['phone'] = user.phone
        data['image'] = user.image.url if user.image else None
        data['dob'] = user.dob.url if user.dob else None
        data['gender'] = user.gender.url if user.gender else None
        
        
        return data
    
    
class Registration(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    image = serializers.FileField(allow_null=True, required=False)  
    dob = serializers.CharField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'name', 'phone', 'email', 'password','image', 
            'dob', 'gender'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)  # This should be a method that hashes the password
        user.set_password(password)  # Ensure the password is hashed
        user.save()
        return user

    
    
class ProfileSer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model=CustomUser
        fields=['id','name', 'phone', 'email', 'dob','image', 'gender', ]
        
    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
    
class MedicationSer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source = 'user.name')
    class Meta:
        model = Medications
        fields = ['id','name','start_date','end_date','time_interval','after_food','user']

        
      
 