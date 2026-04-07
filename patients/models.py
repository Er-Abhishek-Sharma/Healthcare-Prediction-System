"""
Patients App - Models
=====================
Patient records, medical history, and doctor recommendations.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class PatientProfile(models.Model):
    """Extended profile for patients with medical information."""

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')

    # Medical details
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    height = models.FloatField(help_text='Height in cm', blank=True, null=True)
    weight = models.FloatField(help_text='Weight in kg', blank=True, null=True)
    allergies = models.TextField(blank=True, null=True, help_text='Known allergies')
    chronic_conditions = models.TextField(blank=True, null=True, help_text='Existing chronic conditions')
    current_medications = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    insurance_number = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"

    def get_bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight:
            height_m = self.height / 100
            bmi = self.weight / (height_m ** 2)
            return round(bmi, 2)
        return None

    def get_bmi_category(self):
        """Return BMI category."""
        bmi = self.get_bmi()
        if bmi is None:
            return "Unknown"
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"


class Disease(models.Model):
    """Disease catalog with detailed information."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    icd_code = models.CharField(max_length=20, blank=True, help_text='ICD-10 code')

    # Medical recommendations
    precautions = models.TextField(help_text='Comma-separated list of precautions')
    medications = models.TextField(help_text='Common medications (for information only)')
    diet_plan = models.TextField(help_text='Recommended diet')
    exercises = models.TextField(blank=True, help_text='Recommended exercises')

    # Doctor specialization recommendation
    recommended_specialist = models.CharField(max_length=100, blank=True)

    # Risk level
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='medium')

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Disease'
        verbose_name_plural = 'Diseases'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_precautions_list(self):
        """Return precautions as a list."""
        return [p.strip() for p in self.precautions.split(',') if p.strip()]

    def get_medications_list(self):
        """Return medications as a list."""
        return [m.strip() for m in self.medications.split(',') if m.strip()]

    def get_diet_list(self):
        """Return diet items as a list."""
        return [d.strip() for d in self.diet_plan.split(',') if d.strip()]


class Symptom(models.Model):
    """Symptom catalog."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    body_part = models.CharField(max_length=100, blank=True)
    severity_weight = models.IntegerField(
        default=1,
        help_text='Weight for severity calculation (1-10)'
    )

    class Meta:
        verbose_name = 'Symptom'
        verbose_name_plural = 'Symptoms'
        ordering = ['name']

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    """Extended profile for doctors."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialization = models.CharField(max_length=100)
    available_diseases = models.ManyToManyField(Disease, blank=True,
        help_text='Diseases this doctor treats')
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    experience_years = models.IntegerField(default=0)
    available_days = models.CharField(max_length=200, default='Mon-Fri',
        help_text='e.g., Mon-Fri, 9AM-5PM')
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
