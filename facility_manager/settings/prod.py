from .base import *

# ─────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

RAILWAY_PUBLIC_DOMAIN = env("RAILWAY_PUBLIC_DOMAIN", default=None)
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# ─────────────────────────────────────────────
# Security
# ─────────────────────────────────────────────

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")

# ─────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────

DATABASES = {
    "default": env.db("DATABASE_URL")
}
DATABASES["default"]["CONN_MAX_AGE"] = 600

# ─────────────────────────────────────────────
# Static Files — Whitenoise
# ─────────────────────────────────────────────

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

# ─────────────────────────────────────────────
# Media Files — Cloudflare R2
# ─────────────────────────────────────────────

INSTALLED_APPS += ["storages"]

CLOUDFLARE_R2_BUCKET_NAME = env("CLOUDFLARE_R2_BUCKET_NAME")
CLOUDFLARE_R2_ACCOUNT_ID = env("CLOUDFLARE_R2_ACCOUNT_ID")
CLOUDFLARE_R2_ACCESS_KEY = env("CLOUDFLARE_R2_ACCESS_KEY")
CLOUDFLARE_R2_SECRET_KEY = env("CLOUDFLARE_R2_SECRET_KEY")
CLOUDFLARE_R2_PUBLIC_URL = env("CLOUDFLARE_R2_PUBLIC_URL")  # e.g. https://pub-xxx.r2.dev

R2_STORAGE_OPTIONS = {
    "bucket_name": CLOUDFLARE_R2_BUCKET_NAME,
    "access_key": CLOUDFLARE_R2_ACCESS_KEY,
    "secret_key": CLOUDFLARE_R2_SECRET_KEY,
    "endpoint_url": f"https://{CLOUDFLARE_R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    "region_name": "auto",
    "signature_version": "s3v4",
    "default_acl": None,
}

STORAGES["default"] = {
    "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    "OPTIONS": R2_STORAGE_OPTIONS
}

MEDIA_URL = f"{CLOUDFLARE_R2_PUBLIC_URL}/"

# ─────────────────────────────────────────────
# Redis & Celery
# ─────────────────────────────────────────────

REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# ─────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────

INSTALLED_APPS += ["anymail"]

EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"

ANYMAIL = {
    "MAILJET_API_KEY": env("MAILJET_API_KEY"),
    "MAILJET_SECRET_KEY": env("MAILJET_SECRET_KEY"),
}

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@facilitymanager.com")

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}