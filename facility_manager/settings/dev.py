from .base import *

DEBUG = True
ALLOWED_HOSTS = []

# Development email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
