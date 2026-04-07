"""Patients App - Forms"""
from django import forms
from .models import PatientProfile


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg', 'step': '0.1'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
