"""
Predictions App - Views
=======================
Handles symptom input, ML prediction, result display, and history.
"""

import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q

from .models import Prediction, PredictionSymptom, PredictionReport
from patients.models import Disease, Symptom, DoctorProfile
from ml_module.predictor import get_prediction_engine, SYMPTOM_LIST

logger = logging.getLogger(__name__)


# ─── Symptom Selection & Prediction ──────────────────────────────────────────

@login_required
def predict_disease(request):
    """
    Main prediction view.
    GET: Show symptom selection form
    POST: Process symptoms and make ML prediction
    """
    # Organize symptoms alphabetically for the UI
    symptoms = Symptom.objects.all().order_by('name')

    # If no symptoms in DB, create from ML module list
    if not symptoms.exists():
        for sym_name in SYMPTOM_LIST:
            Symptom.objects.get_or_create(
                name=sym_name,
                defaults={'description': f'Symptom: {sym_name.replace("_", " ").title()}'}
            )
        symptoms = Symptom.objects.all().order_by('name')

    if request.method == 'POST':
        selected_symptoms = request.POST.getlist('symptoms')
        age = request.POST.get('age', 25)
        notes = request.POST.get('notes', '')

        if len(selected_symptoms) < 2:
            messages.warning(request, 'Please select at least 2 symptoms for a reliable prediction.')
            return render(request, 'predictions/predict.html', {
                'symptoms': symptoms,
                'title': 'Disease Prediction'
            })

        try:
            # Get ML engine and make prediction
            engine = get_prediction_engine()

            # Check if models are trained
            if engine.best_model is None:
                logger.info("Models not trained. Training now...")
                engine.train_and_evaluate()

            # Main prediction
            prediction_result = engine.predict(selected_symptoms)

            # Compare all models
            model_comparison = engine.compare_all_models(selected_symptoms)

            # Get or create disease in database
            disease_name = prediction_result['predicted_disease']
            disease, _ = Disease.objects.get_or_create(
                name=disease_name,
                defaults={
                    'description': f'Predicted disease: {disease_name}',
                    'precautions': 'Consult a doctor immediately, Rest, Stay hydrated, Monitor symptoms',
                    'medications': 'Consult physician for appropriate medications',
                    'diet_plan': 'Balanced diet, Avoid junk food, Stay hydrated',
                    'risk_level': 'medium',
                }
            )

            # Save prediction to database
            prediction = Prediction.objects.create(
                patient=request.user,
                age=int(age),
                predicted_disease=disease,
                predicted_disease_name=disease_name,
                model_used=prediction_result['model_used'],
                confidence_score=prediction_result['confidence'],
                algorithm_results={
                    k: v.get('test_accuracy', 0)
                    for k, v in engine.accuracy_results.items()
                    if 'error' not in v
                },
                alternative_predictions=prediction_result['top_predictions'],
                additional_notes=notes,
            )

            # Link symptoms to prediction
            for sym_name in selected_symptoms:
                sym_name_clean = sym_name.replace('_', ' ').title()
                symptom_obj = Symptom.objects.filter(
                    Q(name=sym_name) | Q(name=sym_name_clean)
                ).first()
                if symptom_obj:
                    PredictionSymptom.objects.create(
                        prediction=prediction,
                        symptom=symptom_obj,
                        severity=1
                    )

            # Recommend doctors
            recommended_doctors = DoctorProfile.objects.filter(
                specialization__icontains=disease.recommended_specialist or 'General',
                is_available=True
            )[:3]

            context = {
                'prediction': prediction,
                'disease': disease,
                'prediction_result': prediction_result,
                'model_comparison': model_comparison,
                'recommended_doctors': recommended_doctors,
                'selected_symptoms': selected_symptoms,
                'title': 'Prediction Results',
            }
            return render(request, 'predictions/result.html', context)

        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            messages.error(request, f'Prediction error: {str(e)}. Please try again.')

    return render(request, 'predictions/predict.html', {
        'symptoms': symptoms,
        'symptom_list': json.dumps(SYMPTOM_LIST),
        'title': 'Disease Prediction'
    })


@login_required
def prediction_result(request, prediction_id):
    """
    View a specific prediction result.
    Patients can only see their own predictions.
    Doctors and admins can see any prediction.
    """
    user = request.user

    # Doctors and admins can view any prediction; patients only their own
    if user.is_doctor() or user.is_admin_user():
        prediction = get_object_or_404(Prediction, id=prediction_id)
    else:
        prediction = get_object_or_404(Prediction, id=prediction_id, patient=user)

    disease = prediction.predicted_disease

    # Recommend doctors based on disease specialist
    if disease and disease.recommended_specialist:
        recommended_doctors = DoctorProfile.objects.filter(
            specialization__icontains=disease.recommended_specialist,
            is_available=True
        )[:3]
    else:
        recommended_doctors = DoctorProfile.objects.filter(is_available=True)[:3]

    # Build algorithm comparison for the chart
    algorithm_results = prediction.algorithm_results or {}

    context = {
        'prediction': prediction,
        'disease': disease,
        'recommended_doctors': recommended_doctors,
        'algorithm_results': algorithm_results,
        'title': f'Prediction #{prediction.id} — {prediction.predicted_disease_name}',
    }
    return render(request, 'predictions/result.html', context)


@login_required
def prediction_history(request):
    """View all predictions for the current patient."""
    search_query = request.GET.get('q', '')
    predictions = Prediction.objects.filter(patient=request.user)

    if search_query:
        predictions = predictions.filter(
            Q(predicted_disease_name__icontains=search_query) |
            Q(created_at__icontains=search_query)
        )

    predictions = predictions.order_by('-created_at')

    context = {
        'predictions': predictions,
        'search_query': search_query,
        'title': 'Prediction History',
    }
    return render(request, 'predictions/history.html', context)


@login_required
def generate_pdf_report(request, prediction_id):
    """Generate PDF report for a prediction."""
    prediction = get_object_or_404(Prediction, id=prediction_id, patient=request.user)

    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a73e8'),
            alignment=1  # Center
        )
        story.append(Paragraph("🏥 Healthcare Prediction System", title_style))
        story.append(Paragraph("Disease Prediction Report", styles['Heading2']))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a73e8')))
        story.append(Spacer(1, 20))

        # Patient Info
        story.append(Paragraph("Patient Information", styles['Heading3']))
        patient_data = [
            ['Patient Name:', prediction.patient.get_full_name() or prediction.patient.username],
            ['Report ID:', f'#{prediction.id}'],
            ['Date:', prediction.created_at.strftime('%B %d, %Y %H:%M')],
            ['Patient Age:', str(prediction.age)],
        ]
        t = Table(patient_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Prediction Result
        story.append(Paragraph("Prediction Result", styles['Heading3']))
        result_data = [
            ['Predicted Disease:', prediction.predicted_disease_name],
            ['Confidence:', prediction.get_confidence_percentage()],
            ['Model Used:', prediction.model_used],
        ]
        t = Table(result_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Symptoms
        story.append(Paragraph("Reported Symptoms", styles['Heading3']))
        symptom_names = [ps.symptom.name.replace('_', ' ').title()
                         for ps in prediction.predictionsymptom_set.all()]
        if symptom_names:
            for sym in symptom_names:
                story.append(Paragraph(f"• {sym}", styles['Normal']))
        story.append(Spacer(1, 20))

        # Disease Info
        if prediction.predicted_disease:
            disease = prediction.predicted_disease
            story.append(Paragraph("Medical Recommendations", styles['Heading3']))
            story.append(Paragraph("Precautions:", styles['Heading4']))
            for p in disease.get_precautions_list():
                story.append(Paragraph(f"• {p}", styles['Normal']))

            story.append(Spacer(1, 10))
            story.append(Paragraph("Diet Plan:", styles['Heading4']))
            for d in disease.get_diet_list():
                story.append(Paragraph(f"• {d}", styles['Normal']))

        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "⚠️ Disclaimer: This is an AI-generated prediction for informational purposes only. "
            "Please consult a qualified healthcare professional for proper diagnosis and treatment.",
            styles['Italic']
        ))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="prediction_report_{prediction.id}.pdf"'
        return response

    except ImportError:
        messages.error(request, 'PDF generation requires reportlab. Install with: pip install reportlab')
        return redirect('prediction_result', prediction_id=prediction_id)


@login_required
def send_report_email(request, prediction_id):
    """Send prediction report via email."""
    prediction = get_object_or_404(Prediction, id=prediction_id, patient=request.user)

    try:
        from django.core.mail import send_mail
        from django.conf import settings

        subject = f'Healthcare Prediction Report - {prediction.predicted_disease_name}'
        message = f"""
Dear {prediction.patient.get_full_name()},

Your disease prediction report is ready.

Prediction Results:
- Predicted Disease: {prediction.predicted_disease_name}
- Confidence: {prediction.get_confidence_percentage()}
- Date: {prediction.created_at.strftime('%B %d, %Y')}

Please log in to your Healthcare Dashboard to view the full report and recommendations.

⚠️ This is an AI-powered prediction system. Always consult a qualified doctor.

Best regards,
Healthcare Prediction System Team
        """

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [prediction.patient.email],
            fail_silently=False,
        )

        messages.success(request, f'Report sent to {prediction.patient.email}!')

    except Exception as e:
        messages.error(request, f'Could not send email: {str(e)}')

    return redirect('prediction_result', prediction_id=prediction_id)


# ─── Doctor Dashboard ─────────────────────────────────────────────────────────

@login_required
def doctor_dashboard(request):
    """Doctor's dashboard showing all patient predictions for review."""
    if not request.user.is_doctor() and not request.user.is_admin_user():
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('patient_dashboard')

    recent_predictions = Prediction.objects.all().order_by('-created_at')[:20]
    total_patients = Prediction.objects.values('patient').distinct().count()
    total_predictions = Prediction.objects.count()

    context = {
        'recent_predictions': recent_predictions,
        'total_patients': total_patients,
        'total_predictions': total_predictions,
        'title': 'Doctor Dashboard',
    }
    return render(request, 'predictions/doctor_dashboard.html', context)


# ─── AJAX API ─────────────────────────────────────────────────────────────────

@login_required
def get_symptoms_ajax(request):
    """AJAX endpoint for symptom autocomplete."""
    query = request.GET.get('q', '')
    symptoms = Symptom.objects.filter(name__icontains=query)[:20]
    data = [{'id': s.id, 'name': s.name, 'display': s.name.replace('_', ' ').title()} for s in symptoms]
    return JsonResponse({'symptoms': data})
