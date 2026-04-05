"""
Creates a default Admin user on first deploy if none exists.
Credentials are read from environment variables:
  DJANGO_ADMIN_EMAIL
  DJANGO_ADMIN_PASSWORD
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Create a default Admin group user from environment variables if none exists."

    def handle(self, *args, **kwargs):
        import os

        email = os.environ.get("DJANGO_ADMIN_EMAIL")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_ADMIN_EMAIL or DJANGO_ADMIN_PASSWORD not set — skipping."
            ))
            return

        if User.objects.filter(groups__name="Admin").exists():
            self.stdout.write(self.style.SUCCESS(
                "At least one Admin user already exists — skipping."
            ))
            return

        user = User.objects.create_user(email=email, password=password, email_verified=True)

        admin_group, _ = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)

        self.stdout.write(self.style.SUCCESS(
            f'Admin user "{email}" created and assigned to Admin group.'
        ))