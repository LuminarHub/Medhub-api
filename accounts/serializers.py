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
    
    
class DoctorSer(serializers.ModelSerializer):
    hospital_name = serializers.ReadOnlyField(source="hospital.name")
    class Meta:
        model = Doctor
        fields = ['id','name','email','phone','image','dob','gender','rating','department','about','experience','hospital','hospital_name']

class PrescriptionSer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Automatically assigns the logged-in user
    doctor = DoctorSer()

    class Meta:
        model = Prescription
        fields = ['id', 'image', 'doctor', 'date', 'user']

    def create(self, validated_data):
        """
        Override the create method to handle bulk creation of prescriptions.
        """
        # If there are any nested serializer data (e.g., doctor), handle them accordingly
        doctor_data = validated_data.pop('doctor', None)
        if doctor_data:
            # Assuming that you are passing doctor info in the request for each prescription
            validated_data['doctor'] = Doctor.objects.get(id=doctor_data['id'])
        return super().create(validated_data)
    
    
class PrescriptionAddSer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source = 'user.name')
    doctor_name = serializers.ReadOnlyField(source = 'doctor.name')
    class Meta:
        model = Prescription
        fields = ['id','image','doctor','date','user','doctor_name']

        
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
    category = CategorySer()
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