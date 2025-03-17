from django.urls import path
from .views import *

urlpatterns = [
    path('login/',LoginView.as_view()),
    path('registration/',RegistrationStudentView.as_view()),
    path('profile/',ProfileView.as_view()),
    path('profile-update/',ProfileUpdateView.as_view()),
    path('medication/',MediactionAddView.as_view()),
    path('medication-delete/<int:pk>/',MedicationDeleteView.as_view()),
]