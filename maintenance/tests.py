from django.test import TestCase
from django.core.exceptions import ValidationError
from facilities.models import Building, Room
from assets.models import Asset
from maintenance.models import WorkOrder
from maintenance.choices import WorkOrderStatus

class WorkOrderModelTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Build A")
        self.room = Room.objects.create(building=self.building, name="Room 1")
        self.asset = Asset.objects.create(name="AC Unit", room=self.room)

    def test_work_order_validation_fail(self):
        """A work order must reference building, room, or asset."""
        wo = WorkOrder(title="No Location")
        with self.assertRaises(ValidationError):
            wo.full_clean()

    def test_work_order_location_property_asset(self):
        """Test the location property when asset is set."""
        wo = WorkOrder.objects.create(title="Fix AC", asset=self.asset)
        self.assertEqual(wo.location, "Asset: AC Unit")

    def test_work_order_location_property_room(self):
        """Test the location property when room is set (no asset)."""
        wo = WorkOrder.objects.create(title="Clean Floor", room=self.room)
        self.assertEqual(wo.location, "Room: Build A – Room 1")

    def test_work_order_default_status(self):
        """Ensure default status is OPEN."""
        wo = WorkOrder.objects.create(title="Fix Light", building=self.building)
        self.assertEqual(wo.status, WorkOrderStatus.OPEN)
        self.assertEqual(str(wo), "Fix Light (Open)")
