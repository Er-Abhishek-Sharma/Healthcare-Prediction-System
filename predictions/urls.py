"""Predictions App - URL Patterns"""
from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_disease, name='predict_disease'),
    path('result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('report/pdf/<int:prediction_id>/', views.generate_pdf_report, name='generate_pdf_report'),
    path('report/email/<int:prediction_id>/', views.send_report_email, name='send_report_email'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('api/symptoms/', views.get_symptoms_ajax, name='get_symptoms_ajax'),
]
