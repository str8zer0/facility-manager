from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from facilities.models import Building, Room

User = get_user_model()

class FacilityTests(TestCase):
    def setUp(self):
        # Create groups for permissions
        self.staff_group, _ = Group.objects.get_or_create(name="Staff")
        self.manager_group, _ = Group.objects.get_or_create(name="Manager")
        
        # Create users
        self.staff_user = User.objects.create_user(email="staff@example.com", password="password123")
        self.staff_user.groups.add(self.staff_group)
        
        self.manager_user = User.objects.create_user(email="manager@example.com", password="password123")
        self.manager_user.groups.add(self.manager_group)
        
        # Create a building
        self.building = Building.objects.create(
            name="Main Building",
            address="123 Street",
            description="Main HQ"
        )

    def test_building_list_view_staff_access(self):
        """Test that staff can access building list."""
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.get(reverse('facilities:building_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Main Building")

    def test_building_detail_view_staff_access(self):
        """Test that staff can access building detail."""
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.get(reverse('facilities:building_detail', kwargs={'pk': self.building.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Main HQ")

    def test_room_creation(self):
        """Test creating a room for a building."""
        room = Room.objects.create(
            building=self.building,
            name="Room 101",
            floor=1
        )
        self.assertEqual(str(room), "Main Building – Room 101")
        self.assertEqual(self.building.rooms.count(), 1)

    def test_building_create_permission(self):
        """Test that only managers can create buildings (Staff should be denied/redirected)."""
        # Staff access
        self.client.login(email="staff@example.com", password="password123")
        response = self.client.get(reverse('facilities:building_create'))
        self.assertEqual(response.status_code, 403) # Forbidden
        
        # Manager access
        self.client.login(email="manager@example.com", password="password123")
        response = self.client.get(reverse('facilities:building_create'))
        self.assertEqual(response.status_code, 200)
