"""
Patients App - Views
====================
Patient dashboard, medical history, and doctor listing.
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone

from .models import PatientProfile, Disease, DoctorProfile
from .forms import PatientProfileForm
from predictions.models import Prediction


@login_required
def patient_dashboard(request):
    """
    Patient's main dashboard showing:
    - Recent predictions
    - Health stats
    - Quick access to prediction tool
    - Medical history summary
    """
    user = request.user

    # Create patient profile if it doesn't exist
    profile, created = PatientProfile.objects.get_or_create(user=user)

    # Get recent predictions
    recent_predictions = Prediction.objects.filter(
        patient=user
    ).order_by('-created_at')[:5]

    # Statistics
    total_predictions = Prediction.objects.filter(patient=user).count()

    # Disease frequency for chart
    disease_freq = Prediction.objects.filter(patient=user).values(
        'predicted_disease_name'
    ).annotate(count=Count('id')).order_by('-count')[:5]

    disease_labels = json.dumps([d['predicted_disease_name'] for d in disease_freq])
    disease_counts = json.dumps([d['count'] for d in disease_freq])

    # Monthly prediction trend (last 6 months)
    from django.utils import timezone
    import datetime
    months_data = []
    months_labels = []
    for i in range(5, -1, -1):
        month_date = timezone.now() - datetime.timedelta(days=30*i)
        count = Prediction.objects.filter(
            patient=user,
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        months_data.append(count)
        months_labels.append(month_date.strftime('%b %Y'))

    context = {
        'profile': profile,
        'recent_predictions': recent_predictions,
        'total_predictions': total_predictions,
        'disease_labels': disease_labels,
        'disease_counts': disease_counts,
        'months_labels': json.dumps(months_labels),
        'months_data': json.dumps(months_data),
        'bmi': profile.get_bmi(),
        'bmi_category': profile.get_bmi_category(),
        'title': 'Patient Dashboard',
    }
    return render(request, 'patients/dashboard.html', context)


@login_required
def update_patient_profile(request):
    """Update patient medical profile."""
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medical profile updated successfully!')
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=profile)

    return render(request, 'patients/update_profile.html', {
        'form': form,
        'title': 'Update Medical Profile'
    })


@login_required
def doctor_list(request):
    """List all available doctors with filtering."""
    specialization = request.GET.get('specialization', '')
    search = request.GET.get('q', '')

    doctors = DoctorProfile.objects.filter(
        user__is_active=True,
        is_available=True
    )

    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(specialization__icontains=search)
        )

    # Get unique specializations for filter
    specializations = DoctorProfile.objects.values_list(
        'specialization', flat=True
    ).distinct()

    context = {
        'doctors': doctors,
        'specializations': specializations,
        'selected_spec': specialization,
        'search': search,
        'title': 'Find a Doctor',
    }
    return render(request, 'patients/doctor_list.html', context)


@login_required
def medical_history(request):
    """View complete medical history for the patient."""
    search = request.GET.get('q', '')
    predictions = Prediction.objects.filter(patient=request.user)

    if search:
        predictions = predictions.filter(
            Q(predicted_disease_name__icontains=search) |
            Q(additional_notes__icontains=search)
        )

    predictions = predictions.order_by('-created_at')

    context = {
        'predictions': predictions,
        'search': search,
        'title': 'Medical History',
    }
    return render(request, 'patients/medical_history.html', context)


@login_required
def disease_info(request, disease_id):
    """View detailed information about a disease."""
    disease = get_object_or_404(Disease, id=disease_id)
    doctors = DoctorProfile.objects.filter(
        specialization__icontains=disease.recommended_specialist or '',
        is_available=True
    )[:5]

    context = {
        'disease': disease,
        'doctors': doctors,
        'title': disease.name,
    }
    return render(request, 'patients/disease_info.html', context)
