"""Patients Admin"""
from django.contrib import admin
from .models import PatientProfile, Disease, Symptom, DoctorProfile


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'risk_level', 'recommended_specialist']
    list_filter = ['risk_level', 'category']
    search_fields = ['name', 'description']


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'body_part', 'severity_weight']
    search_fields = ['name']


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'height', 'weight']
    search_fields = ['user__username', 'user__email']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'rating', 'is_available']
    list_filter = ['is_available', 'specialization']
