from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

class LoginView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

class RegistrationStudentView(APIView):
    @swagger_auto_schema(
        request_body=Registration,    
        responses={
            200:openapi.Response('Registration Successfull....',Registration),
            400: 'Validation errors'
        }
    )
    def post(self,request):
        try:
            ser=Registration(data=request.data)
            if ser.is_valid():    
                user = ser.save()
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                return Response(data={"Status": "Success", "Msg": "Registration Successful!!!!", "data": ser.data,"tokens": {
                            "access": access_token,
                            "refresh": refresh_token
                        }}, status=status.HTTP_200_OK)
            else:
                return Response(data={"Status":"Failed","Msg":"Registration Unsuccessfull....","Errors":ser.errors},status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_400_BAD_REQUEST)
   
   
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user_id=request.user.id
            print(user_id)
            profile=CustomUser.objects.get(id=user_id)
            print(profile)
            ser=ProfileSer(profile)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    @swagger_auto_schema(
        request_body=ProfileSer,    
        responses={
            200:openapi.Response('Profile Updated....',ProfileSer),
            400: 'Validation errors'
        }
    )
    def put(self,request,**kwargs):
        try:
            profile=CustomUser.objects.get(id=request.user.id)
            ser=ProfileSer(profile,data=request.data,partial=True) 
            if ser.is_valid():
                ser.save()  
                return Response(data={"Status":"Success","Msg":"Profile updated successfully","data": ser.data},status=status.HTTP_200_OK)
            else:
                return Response(data={"Status": "Failed", "Msg": "Invalid data", "Errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response(
                data={"Status": "Failed", "Msg": "Profile not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                data={"Status": "Failed", "Msg": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AllDoctorsView(APIView):
    def get(self,request):
        try:
            doc = Doctor.objects.all()
            ser = DoctorSer(doc,many=True)
            print("doctors",ser.data)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)

class MediactionAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user_id=request.user.id
            user=CustomUser.objects.get(id=user_id)
            medication  = Medications.objects.filter(user=user)
            ser = MedicationSer(medication,many=True)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)
    def post(self, request):
        try:
            medications_data = request.data.get("data", [])
            print("mmm",medications_data)
            if not isinstance(medications_data, list):
                return Response({"Status": "Failed", "Msg": "Expected a list of medications."}, status=status.HTTP_400_BAD_REQUEST)
            successful_medications = []
            failed_medications = []
            
            for medication_data in medications_data:
                print(",,,,,,,",medication_data)
                ser = MedicationSer(data=medication_data)
                print("=======",ser)
                if ser.is_valid():    
                    ser.save(user=request.user)
                    successful_medications.append(ser.data)
                else:
                    failed_medications.append({
                        "data": medication_data,
                        "errors": ser.errors
                    })
            success_response={}
            failure_response = {}
            # Construct the response based on successes and failures
            if successful_medications:
                success_response = {"Status": "Success", "Msg": f"{len(successful_medications)} Medications Added Successfully!", "data": successful_medications}
            
            if failed_medications:
                failure_response = {"Status": "Failed", "Msg": f"{len(failed_medications)} Medications Failed to Add", "Errors": failed_medications}
            
            # Combine both success and failure responses
            response_data = {**success_response, **failure_response}
            return Response(data=response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("eeeeeee",e)
            return Response({"Status": "Failed", "Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   


class MedicationDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def delete(self,request,**kwargs):
        try:
            med_id=kwargs.get('pk')
            med=Medications.objects.get(id=med_id)
            if med.user!=request.user:
                return Response(data={"Status":"Failed","Msg":"Unauthorized access: You do not have permission to delete this trip."},status=status.HTTP_401_UNAUTHORIZED)
            med.delete()
            return Response({"Status":"Success","Msg":f"{med.name} Medicine Deleted Successfully!!!!!"})
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrescriptionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user=request.user.id
            prescriptions = Prescription.objects.filter(user=user).order_by('-date')
            ser = PrescriptionSer(prescriptions,many=True)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)
    def post(self,request):
        try:
            ser=PrescriptionAddSer(data=request.data)
            if ser.is_valid():    
                ser.save(user=request.user)
                return Response(data={"Status": "Success", "Msg": "Prescription Added Successful!!!!", "data": ser.data}, status=status.HTTP_200_OK)
            else:
                return Response(data={"Status":"Failed","Msg":"Not Added  successfully....","Errors":ser.errors},status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_400_BAD_REQUEST)
   


class PrescriptionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def put(self,request,**kwargs):
        try:
            pres_id = kwargs.get('pk')
            prescription=Prescription.objects.get(id=pres_id)
            ser=PrescriptionAddSer(prescription,data=request.data,partial=True) 
            if ser.is_valid():
                ser.save()  
                return Response(data={"Status":"Success","Msg":"prescription updated successfully","data": ser.data},status=status.HTTP_200_OK)
            else:
                return Response(data={"Status": "Failed", "Msg": "Invalid data", "Errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        except prescription.DoesNotExist:
            return Response(
                data={"Status": "Failed", "Msg": "prescription not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                data={"Status": "Failed", "Msg": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request,**kwargs):
        try:
            pres_id=kwargs.get('pk')
            pre=Prescription.objects.get(id=pres_id)
            if pre.user!=request.user:
                return Response(data={"Status":"Failed","Msg":"Unauthorized access: You do not have permission to delete this prescription."},status=status.HTTP_401_UNAUTHORIZED)
            pre.delete()
            return Response({"Status":"Success","Msg":" Prescription Deleted Successfully!!!!!"})
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class EmergencyContactView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user=request.user.id
            contact = EmergencyContact.objects.filter(user=user).order_by('-created_at')
            ser = EmergencyContactSer(contact,many=True)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)
    def post(self,request):
        try:
            ser=EmergencyContactSer(data=request.data)
            if ser.is_valid():    
                ser.save(user=request.user)
                return Response(data={"Status": "Success", "Msg": "Contact Added Successful!!!!", "data": ser.data}, status=status.HTTP_200_OK)
            else:
                return Response(data={"Status":"Failed","Msg":"Not Added  successfully....","Errors":ser.errors},status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_400_BAD_REQUEST)
   


class EmergencyContactDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def put(self,request,**kwargs):
        try:
            con_id = kwargs.get('pk')
            contact=EmergencyContact.objects.get(id=con_id)
            ser=EmergencyContactSer(contact,data=request.data,partial=True) 
            if ser.is_valid():
                ser.save()  
                return Response(data={"Status":"Success","Msg":"EmergencyContact updated successfully","data": ser.data},status=status.HTTP_200_OK)
            else:
                return Response(data={"Status": "Failed", "Msg": "Invalid data", "Errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        except EmergencyContact.DoesNotExist:
            return Response(
                data={"Status": "Failed", "Msg": "EmergencyContact not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                data={"Status": "Failed", "Msg": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request,**kwargs):
        try:
            pres_id=kwargs.get('pk')
            pre=EmergencyContact.objects.get(id=pres_id)
            if pre.user!=request.user:
                return Response(data={"Status":"Failed","Msg":"Unauthorized access: You do not have permission to delete this Contact."},status=status.HTTP_401_UNAUTHORIZED)
            pre.delete()
            return Response({"Status":"Success","Msg":" Contact Deleted Successfully!!!!!"})
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HospitalAllView(APIView):
    def get(self,request,**kwargs):
        try:
            hospitals = Hospital.objects.all()
            ser = HospitalSer(hospitals,many=True)
            print("Hospitals",ser.data)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)
        
        
        
        

class MyBookingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user=request.user.id
            contact = Booking.objects.filter(user=user).order_by('-created_at')
            ser = BookingGetSer(contact,many=True)
            print("all doctors get data",ser.data)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)
    def post(self,request):
        try:
            ser=BookingSer(data=request.data)
            if ser.is_valid():    
                ser.save(user=request.user)
                
                Notification.objects.create(user=request.user,message="Booked Successfully")

                return Response(data={"Status": "Success", "Msg": "Booked  Successful!!!!", "data": ser.data}, status=status.HTTP_200_OK)
            else:
                return Response(data={"Status":"Failed","Msg":"Unsuccessful....","Errors":ser.errors},status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_400_BAD_REQUEST)
   


class MyBookingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def put(self,request,**kwargs):
        try:
            con_id = kwargs.get('pk')
            contact=Booking.objects.get(id=con_id)
            ser=BookingSer(contact,data=request.data,partial=True) 
            if ser.is_valid():
                ser.save()  
                return Response(data={"Status":"Success","Msg":"Booking updated successfully","data": ser.data},status=status.HTTP_200_OK)
            else:
                return Response(data={"Status": "Failed", "Msg": "Invalid data", "Errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        except Booking.DoesNotExist:
            return Response(
                data={"Status": "Failed", "Msg": "Booking not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                data={"Status": "Failed", "Msg": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request,**kwargs):
        try:
            book_id=kwargs.get('pk')
            bk=Booking.objects.get(id=book_id)
            if bk.user!=request.user:
                return Response(data={"Status":"Failed","Msg":"Unauthorized access: You do not have permission to delete this booking."},status=status.HTTP_401_UNAUTHORIZED)
            bk.delete()
            return Response({"Status":"Success","Msg":" booking Deleted Successfully!!!!!"})
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from datetime import time  

class ReminderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user=request.user.id
            rem = Reminder.objects.filter(user=user).order_by('-created_at')
            ser = ReminderSerializer(rem,many=True)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)
    def post(self,request):
        try:
            reminder_data = request.data
            time_data = reminder_data.get('time')  
            
            if time_data:
                reminder_time = time(hour=time_data['hour'], minute=time_data['minute'], second=time_data['second'])
                reminder_data['time'] = reminder_time

            ser = ReminderSerializer(data=reminder_data)
            if ser.is_valid():    
                ser.save(user=request.user)
                
                Notification.objects.create(user=request.user,message="Reminder Added  Successful!!!!")
                return Response(data={"Status": "Success", "Msg": "Reminder Added  Successful!!!!", "data": ser.data}, status=status.HTTP_200_OK)
            else:
                return Response(data={"Status":"Failed","Msg":"Unsuccessful....","Errors":ser.errors},status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_400_BAD_REQUEST)
   


class ReminderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def put(self,request,**kwargs):
        try:
            rem_id = kwargs.get('pk')
            reminder=Reminder.objects.get(id=rem_id)
            ser=ReminderSerializer(reminder,data=request.data,partial=True) 
            if ser.is_valid():
                ser.save()  
                Notification.objects.create(user=request.user,message="Reminder Updated  Successfully!!!!")

                return Response(data={"Status":"Success","Msg":"Reminder updated successfully","data": ser.data},status=status.HTTP_200_OK)
            else:
                return Response(data={"Status": "Failed", "Msg": "Invalid data", "Errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        except Reminder.DoesNotExist:
            return Response(
                data={"Status": "Failed", "Msg": "Reminder not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                data={"Status": "Failed", "Msg": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self,request,**kwargs):
        try:
            rem_id=kwargs.get('pk')
            rem=Reminder.objects.get(id=rem_id)
            if rem.user!=request.user:
                return Response(data={"Status":"Failed","Msg":"Unauthorized access: You do not have permission to delete this Reminder."},status=status.HTTP_401_UNAUTHORIZED)
            rem.delete()
            Notification.objects.create(user=request.user,message="Reminder Deleted!!!!")

            return Response({"Status":"Success","Msg":" Reminder Deleted Successfully!!!!!"})
        except Exception as e:
            return Response({"Status":"Failed","Error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request):
        try:
            user=request.user.id
            rem = Notification.objects.filter(user=user).order_by('-created_at')
            ser = NotificationSerializer(rem,many=True)
            print("notifications",ser.data)
            return Response(data={"Status":"Success","data":ser.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"Status":"Failed","Msg":str(e)},status=status.HTTP_404_NOT_FOUND)



class DoctorSearchAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        # Get query parameters
        name = request.query_params.get('name', None)
        department = request.query_params.get('department', None)
        hospital_name = request.query_params.get('hospital_name', None)
        rating = request.query_params.get('rating', None)
        experience = request.query_params.get('experience', None)

        # Filter doctors based on query parameters
        doctors = Doctor.objects.all()

        if name:
            doctors = doctors.filter(name__icontains=name)
        if department:
            doctors = doctors.filter(department__icontains=department)
        if hospital_name:
            doctors = doctors.filter(hospital__name__icontains=hospital_name)
        if rating:
            doctors = doctors.filter(rating__gte=rating)
        if experience:
            doctors = doctors.filter(experience__gte=experience)

        # Serialize the filtered doctors
        serializer = DoctorSer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from django.utils import timezone
from datetime import timedelta

def check_and_send_notifications():
    current_time = timezone.now()
    reminders = Reminder.objects.filter(from_date__lte=current_time.date(), to_date__gte=current_time.date())
    for reminder in reminders:
        reminder_time = timezone.datetime.combine(current_time.date(), reminder.time)
        if reminder_time <= current_time <= reminder_time + timedelta(minutes=1):
            notification = Notification.objects.create(message=reminder.message)
            print(f"Reminder Notification: {notification.message}")
            if reminder.repeat:
                pass
            
            
from django.http import HttpResponse,JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import os

class UserReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user  

        bookings = Booking.objects.filter(user=user)
        prescriptions = Prescription.objects.filter(user=user)
        medications = Medications.objects.filter(user=user)
        emergency = EmergencyContact.objects.filter(user=user)
        for prescription in prescriptions:
            if prescription.image:
                prescription.image_url = request.build_absolute_uri(prescription.image.url)
            else:
                prescription.image_url = None

        html_string = render_to_string('report_template.html', {
            'user': user,
            'bookings': bookings,
            'prescriptions': prescriptions,
            'medications': medications,
            'emergency': emergency,
        })
        pdf_dir = os.path.join(settings.MEDIA_ROOT, "pdf_reports")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filename = f"user_report_{user.id}.pdf"
        pdf_filepath = os.path.join(pdf_dir, pdf_filename)
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(pdf_filepath)
        pdf_url = request.build_absolute_uri(settings.MEDIA_URL + f"pdf_reports/{pdf_filename}")

        return JsonResponse({"data": pdf_url},status=status.HTTP_200_OK)
    
    
    
    
    


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Doctor, Booking, Facilities, Prescription, Hospital

@staff_member_required
def hospital_dashboard(request):
    # If user is a doctor, get their hospital
    if hasattr(request.user, 'doctor'):
        hospital = request.user.doctor.hospital
    elif hasattr(request.user, 'hospital'):
        hospital = request.user.hospital
    else:
        # For superusers, just get the first hospital
        hospital = Hospital.objects.first()
    
    # Get counts for dashboard
    today = timezone.now().date()
    total_doctors = Doctor.objects.filter(hospital=hospital).count()
    total_facilities = Facilities.objects.filter(hospital=hospital).count()
    pending_bookings = Booking.objects.filter(doctor__hospital=hospital, selected_date__gte=today).count()
    today_bookings = Booking.objects.filter(doctor__hospital=hospital, selected_date=today).count()
    recent_prescriptions = Prescription.objects.filter(doctor__hospital=hospital).order_by('-date')[:5].count()
    
    context = {
        'hospital': hospital,
        'total_doctors': total_doctors,
        'total_facilities': total_facilities,
        'pending_bookings': pending_bookings,
        'today_bookings': today_bookings,
        'recent_prescriptions': recent_prescriptions,
    }
    
    return render(request, 'admin/hospital_dashboard.html', context)   
    
