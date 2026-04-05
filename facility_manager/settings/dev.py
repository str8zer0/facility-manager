from .base import *

DEBUG = True
ALLOWED_HOSTS = []

# Development email backend with MailHog
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
