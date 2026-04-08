from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from assets.models import Asset
from maintenance.models import WorkOrder
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class APITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="apiuser@example.com", password="password123")
        self.manager_group, _ = Group.objects.get_or_create(name="Manager")
        self.user.groups.add(self.manager_group)
        self.client.force_authenticate(user=self.user)
        
        self.asset = Asset.objects.create(name="Test Asset")

    def test_asset_list(self):
        """Test listing assets via API."""
        response = self.client.get(reverse('api:asset-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Asset")

    def test_asset_detail(self):
        """Test retrieving a single asset via API."""
        response = self.client.get(reverse('api:asset-detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Asset")

    def test_work_order_create_invalid(self):
        """Test creating a work order without building/room/asset should fail (per serializer validation)."""
        data = {
            "title": "Broken something",
            "description": "It's broken"
        }
        response = self.client.post(reverse('api:work-order-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_work_order_create_valid(self):
        """Test creating a work order with an asset."""
        data = {
            "title": "Repair Asset",
            "asset_id": self.asset.id
        }
        response = self.client.post(reverse('api:work-order-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkOrder.objects.count(), 1)
        self.assertEqual(WorkOrder.objects.first().title, "Repair Asset")

    def test_work_order_comment_api(self):
        """Test adding a comment to a work order via API."""
        wo = WorkOrder.objects.create(title="WO", asset=self.asset, created_by=self.user)
        data = {"comment": "Starting work now"}
        url = reverse('api:work-order-comments', kwargs={'pk': wo.pk})
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(wo.comments.count(), 1)
