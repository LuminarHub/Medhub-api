from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Doctor, CustomUser, Hospital, TimeSlots, Booking

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'phone', 'gender', 'dob', 'image')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'phone', 'gender', 'dob', 'image', 'is_active', 'is_staff')

class DoctorCreationForm(UserCreationForm):
    class Meta:
        model = Doctor
        fields = ('name', 'email', 'phone', 'department', 'hospital', 'experience', 'rating', 'about', 'gender', 'dob', 'image')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # Doctors should have access to admin
        if commit:
            user.save()
        return user

class DoctorChangeForm(UserChangeForm):
    class Meta:
        model = Doctor
        fields = ('name', 'email', 'phone', 'department', 'hospital', 'experience', 'rating', 'about', 'gender', 'dob', 'image', 'is_active')

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlots
        fields = ('slot', 'doctor')
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is not a superuser and is a doctor, limit doctors to the hospital
        if user and not user.is_superuser and hasattr(user, 'doctor'):
            self.fields['doctor'].queryset = Doctor.objects.filter(
                hospital=user.doctor.hospital
            )

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('user', 'doctor', 'category', 'selected_date', 'selected_time')
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is not a superuser and is a doctor, limit doctors to the hospital
        if user and not user.is_superuser and hasattr(user, 'doctor'):
            self.fields['doctor'].queryset = Doctor.objects.filter(
                hospital=user.doctor.hospital
            )
