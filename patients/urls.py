"""Patients App - URL Patterns"""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('profile/update/', views.update_patient_profile, name='update_patient_profile'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('history/', views.medical_history, name='medical_history'),
    path('disease/<int:disease_id>/', views.disease_info, name='disease_info'),
]
