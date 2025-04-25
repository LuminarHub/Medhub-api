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
    
    
class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlots
        fields = ['id', 'slot', 'created_at']
  
  
    
class DoctorSer(serializers.ModelSerializer):
    hospital_name = serializers.ReadOnlyField(source="hospital.name")
    timeslots = TimeSlotSerializer(many=True, read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'email', 'phone', 'image', 'dob', 'gender', 'rating', 'department', 'about', 'experience', 'hospital', 'hospital_name', 'timeslots']

class PrescriptionSer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source = 'user.name')
    class Meta:
        model = Prescription
        fields = ['id','image','doctor','date','user']
    
class PrescriptionAddSer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source = 'user.name')
    class Meta:
        model = Prescription
        fields = ['id','image','doctor','date','user']

        
class EmergencyContactSer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source = 'user.name')
    class Meta:
        model = EmergencyContact
        fields = '__all__'
 
 
class FacilitySer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = '__all__'
 
class BookingSer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
 
class CategorySer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
 
class BookingGetSer(serializers.ModelSerializer):
    doctor = DoctorSer()
    class Meta:
        model = Booking
        fields = '__all__'

class HospitalSer(serializers.ModelSerializer):
    doctors = DoctorSer(many=True)  # This will list all doctors in the hospital
    facilities = FacilitySer(many=True)
    class Meta:
        model = Hospital
        fields = ['id','name','location','rating','about','image','doctors','facilities']
        
        

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'message', 'repeat', 'time', 'from_date', 'to_date', 'created_at']
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']
        
        
class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking  # Example model
        fields = "__all__"  # Include all fields

# Add these to your existing serializers.py file

from rest_framework import serializers
from .models import Doctor, Hospital, CustomUser
from django.contrib.auth.hashers import make_password

class HospitalAdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone', 'password', 'confirm_password']
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['is_staff'] = True
        return CustomUser.objects.create(**validated_data)

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Doctor
        fields = ['name', 'email', 'phone', 'department', 'about', 'experience', 
                 'hospital', 'password', 'confirm_password']
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        doctor = Doctor(**validated_data)
        doctor.set_password(password)
        doctor.is_staff = True
        doctor.save()
        return doctor