"""
Healthcare Prediction System - URL Configuration
================================================
Main URL router for the entire project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='base/home.html'), name='home'),

    # Accounts (auth) URLs
    path('accounts/', include('accounts.urls')),

    # Patients URLs
    path('patients/', include('patients.urls')),

    # Predictions URLs
    path('predictions/', include('predictions.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'healthcare_project.views.error_404'
handler500 = 'healthcare_project.views.error_500'
