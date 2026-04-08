from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Profile

User = get_user_model()

class UserAccountTests(TestCase):
    def test_user_creation(self):
        """Test creating a regular user and ensuring profile is created via signal."""
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123"
        )
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        # Check if profile was created via signal
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_superuser_creation(self):
        """Test creating a superuser."""
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123"
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.email_verified)

    def test_login_view(self):
        """Test the login view status code and template."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_dashboard_redirect_for_anonymous_user(self):
        """Test that dashboard redirects to login for anonymous users."""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_user_role_property(self):
        """Test the role property on User model."""
        user = User.objects.create_user(email="staff@example.com", password="password")
        # Manually create groups since post_migrate might not have run for all groups in test env if not careful,
        # but signals.py has a post_migrate receiver.
        from django.contrib.auth.models import Group
        staff_group, _ = Group.objects.get_or_create(name="Staff")
        user.groups.add(staff_group)
        
        # Refresh from db to ensure role property picks up changes if cached
        user = User.objects.get(email="staff@example.com")
        self.assertEqual(user.role, "STAFF")

        admin_user = User.objects.create_superuser(email="super@example.com", password="password")
        self.assertEqual(admin_user.role, "ADMIN")
