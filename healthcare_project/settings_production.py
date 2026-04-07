"""
Production Settings for HealthPredict AI
==========================================
Use this for Heroku / Render / VPS deployment.
Set environment variables instead of hardcoding secrets.
"""

from .settings import *
import os

# ── Security ─────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']  # Must be set in environment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ── Database (PostgreSQL for production) ─────────────────────────
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ── Static Files (WhiteNoise) ─────────────────────────────────────
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Email (Production SMTP) ───────────────────────────────────────
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# ── Security Headers ──────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
