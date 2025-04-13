from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from .models import (
    CustomUser, Hospital, Facilities, Doctor, TimeSlots, Categories,
    Booking, Prescription, Medications, EmergencyContact, Reminder, Notification
)

# Custom Admin Site
class HospitalAdminSite(admin.AdminSite):
    site_header = 'Hospital Management System'
    site_title = 'Hospital Admin Portal'
    index_title = 'Hospital Management Dashboard'

hospital_admin_site = HospitalAdminSite(name='hospital_admin')

# Custom Form for Login
class HospitalLoginForm(forms.Form):
    username = forms.CharField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)


# Hospital Admin
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'rating', 'hospital_image', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('created_at', 'rating')
    readonly_fields = ('hospital_image_preview',)

    fieldsets = (
        ('Hospital Information', {
            'fields': ('name', 'location', 'rating', 'about', 'image', 'hospital_image_preview')
        }),
    )

    def hospital_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    hospital_image.short_description = 'Image'

    def hospital_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="300" />', obj.image.url)
        return '-'
    hospital_image_preview.short_description = 'Image Preview'


# Facilities Admin
class FacilitiesAdmin(admin.ModelAdmin):
    list_display = ('facility', 'hospital', 'created_at')
    search_fields = ('facility', 'hospital__name')
    list_filter = ('created_at', 'hospital')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_staff:
            return qs.filter(hospital__doctors=request.user)
        return None


# Doctor Admin
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'department', 'experience', 'rating', 'doctor_image')
    search_fields = ('name', 'email', 'department')
    list_filter = ('department', 'experience', 'rating', 'hospital')
    readonly_fields = ('doctor_image_preview',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone',  'image', 'doctor_image_preview', 'dob', 'gender')
        }),
        ('Professional Information', {
            'fields': ('department', 'about', 'experience', 'rating', 'hospital')
        }),
        ('User Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )

    def doctor_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    doctor_image.short_description = 'Image'

    def doctor_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="300" />', obj.image.url)
        return '-'
    doctor_image_preview.short_description = 'Image Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        if request.user.is_hospital:
            return qs.filter(hospital=request.user.id)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:  
            if not obj.password:
                obj.set_password('doctor123')
        elif 'password' in form.changed_data and form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data.get('password'))
        super().save_model(request, obj, form, change)


# TimeSlots Admin
class TimeSlotsAdmin(admin.ModelAdmin):
    list_display = ('slot', 'doctor', 'created_at')
    search_fields = ('slot', 'doctor__name')
    list_filter = ('created_at', 'doctor')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        if request.user.is_hospital:
            return qs.filter(doctor__hospital=request.user.id)
        return qs


# Categories Admin
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Booking Admin
class BookingAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'user', 'category', 'selected_date', 'selected_time', 'created_at')
    search_fields = ('doctor__name', 'user__name', 'category__name')
    list_filter = ('selected_date', 'created_at', 'doctor', 'category')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        if request.user.is_hospital:
            return qs.filter(doctor__hospital=request.user.id)
        return qs


# Prescription Admin
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'user', 'date', 'prescription_image')
    search_fields = ('doctor__name', 'user__name')
    list_filter = ('date', 'doctor')
    readonly_fields = ('prescription_image_preview',)

    def prescription_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    prescription_image.short_description = 'Image'

    def prescription_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="300" />', obj.image.url)
        return '-'
    prescription_image_preview.short_description = 'Image Preview'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        if request.user.is_hospital:
            return qs.filter(Q(doctor__hospital=request.user.id) | Q(doctor=request.user))
        return qs


# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'is_staff')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_active', 'is_staff', 'gender')

    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'password', 'image', 'dob', 'gender')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser','is_hospital')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)


# Register models with the main admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Facilities, FacilitiesAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(TimeSlots, TimeSlotsAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Medications)
admin.site.register(EmergencyContact)
admin.site.register(Reminder)
admin.site.register(Notification)

# Register models with the hospital admin site
hospital_admin_site.register(Doctor, DoctorAdmin)
hospital_admin_site.register(Facilities, FacilitiesAdmin)
hospital_admin_site.register(TimeSlots, TimeSlotsAdmin)
hospital_admin_site.register(Booking, BookingAdmin)
hospital_admin_site.register(Prescription, PrescriptionAdmin)
hospital_admin_site.register(Categories, CategoriesAdmin)
