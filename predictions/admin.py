"""Predictions Admin"""
from django.contrib import admin
from .models import Prediction, PredictionSymptom, PredictionReport


class PredictionSymptomInline(admin.TabularInline):
    model = PredictionSymptom
    extra = 0


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'predicted_disease_name', 'confidence_score', 'model_used', 'created_at']
    list_filter = ['model_used', 'status', 'created_at']
    search_fields = ['patient__username', 'predicted_disease_name']
    inlines = [PredictionSymptomInline]
    readonly_fields = ['created_at', 'updated_at']
