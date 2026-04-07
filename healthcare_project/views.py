"""
Custom error views for the Healthcare Prediction System.
"""
from django.shortcuts import render


def error_404(request, exception):
    """Handle 404 - Page Not Found errors."""
    return render(request, 'base/404.html', status=404)


def error_500(request):
    """Handle 500 - Internal Server Error."""
    return render(request, 'base/500.html', status=500)
