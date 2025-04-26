from django.urls import path
from .views import *

urlpatterns = [
    path('login/',LoginView.as_view()),
    path('registration/',RegistrationStudentView.as_view()),
    path('profile/',ProfileView.as_view()),
    path('profile-update/',ProfileUpdateView.as_view()),
    path('medication/',MediactionAddView.as_view()),
    path('medication/<int:pk>/',MedicationDeleteView.as_view()),
    path('prescription/',PrescriptionView.as_view()),
    path('prescription/<int:pk>/',PrescriptionDetailView.as_view()),
    path('contact/',EmergencyContactView.as_view()),
    path('contact/<int:pk>/',EmergencyContactDetailView.as_view()),
    path('mybooking/',MyBookingView.as_view()),
    path('mybooking/<int:pk>/',MyBookingDetailView.as_view()),
    path('reminder/',ReminderView.as_view()),
    path('reminder/<int:pk>/',ReminderDetailView.as_view()),
    path('notification/',NotificationsView.as_view()),
    path('search/',DoctorSearchAPIView.as_view()),
    path('user-report/', UserReportPDFView.as_view()),
    
    path('doctors-all/',AllDoctorsView.as_view()),
    path('hospitals-all/',HospitalAllView.as_view()),
]