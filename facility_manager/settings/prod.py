from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Security settings for production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Production email backend (SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Persistent DB connections
DATABASES["default"]["CONN_MAX_AGE"] = 600
