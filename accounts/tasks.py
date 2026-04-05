from celery import shared_task
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, user_id):
    """
    Send an email verification link to a newly registered user.
    The link is signed and expires after 24 hours.
    """
    try:
        from accounts.models import User
        user = User.objects.get(pk=user_id)

        if user.email_verified:
            return

        signer = TimestampSigner()
        token = signer.sign(user.pk)

        # Build the verification URL
        base_url = settings.SITE_URL.rstrip("/")
        verification_url = f"{base_url}/accounts/verify-email/{token}/"

        subject = "Verify your Facility Manager account"
        message = f"""
Hi,

Thank you for registering with Facility Manager.

Please verify your email address by clicking the link below:

{verification_url}

This link expires in 24 hours.

If you did not register for this account, please ignore this email.

This is an automated notification.
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    except Exception as exc:
        raise self.retry(exc=exc)