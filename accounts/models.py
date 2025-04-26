from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta
from django.utils import timezone
from .validators import *
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None , **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone=models.BigIntegerField(unique=True,validators=[validate_phone])
    image =  models.FileField(upload_to="profile_image",null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=200,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_hospital = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone']

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def _str_(self):
        return self.email



    
class Hospital(models.Model):
    user= models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='hospital_users',null=True,blank=True)
    name = models.CharField(max_length=300)
    location = models.CharField(max_length=300)
    rating = models.IntegerField()
    about  = models.TextField()
    image = models.FileField(upload_to='hospital_image')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    

class Facilities(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='facilities')
    facility = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.facility} - {self.hospital.name}"


class Doctor(CustomUser):
    rating = models.IntegerField(null=True,blank=True)
    department = models.CharField(max_length=200,null=True,blank=True)
    about = models.TextField()
    experience = models.IntegerField()
    hospital =models.ForeignKey(Hospital,on_delete=models.CASCADE,related_name='doctors')
    
    
    def __str__(self):
        return self.name
    
class TimeSlots(models.Model):
    slot = models.CharField(max_length=200)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE, related_name='timeslots')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return self.slot
    
    
class Categories(models.Model):
    name = models.CharField(max_length=300)
    
    def __str__(self):
        return self.name 

class Booking(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='book_user',null=True)
    category = models.ForeignKey(Categories,on_delete=models.CASCADE)
    selected_date = models.DateField()
    selected_time = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='pres_user',null=True)
    image = models.FileField(upload_to='prescription_images')
    date = models.DateField(auto_now_add=True)
    
    
class Medications(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    time_interval = models.CharField(max_length=200)
    after_food = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class EmergencyContact(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=300)
    relationship = models.CharField(max_length=300)
    phone = models.IntegerField()
    email = models.EmailField()
    options = (
        ('1','High'),
        ('2','Medium'),
        ('3','Low')
    )
    priority = models.CharField(max_length=300 , choices=options)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name 
    
    
class Reminder(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    message = models.TextField()
    repeat = models.BooleanField(default=False)
    time = models.TimeField()
    from_date = models.DateField()
    to_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message
    
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)