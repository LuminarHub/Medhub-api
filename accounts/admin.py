from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(CustomUser)
admin.site.register(Doctor)
admin.site.register(Hospital)
admin.site.register(Facilities)
admin.site.register(TimeSlots)
admin.site.register(Prescription)
admin.site.register(Medications)
admin.site.register(Notification)
admin.site.register(Booking)
admin.site.register(Categories)
admin.site.register(EmergencyContact)
admin.site.register(Reminder)