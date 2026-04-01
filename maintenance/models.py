from django.core.exceptions import ValidationError
from django.db import models
from accounts.models import User
from assets.models import Asset
from common.models import History
from facilities.models import Building, Room
from maintenance.choices import WorkOrderStatus, WorkOrderPriority, ResultStatus, InspectionStatus


class WorkOrder(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders"
    )

    status = models.CharField(
        max_length=20,
        choices=WorkOrderStatus,
        default=WorkOrderStatus.OPEN
    )
    priority = models.CharField(
        max_length=2,
        choices=WorkOrderPriority,
        default=WorkOrderPriority.MEDIUM
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_work_orders"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_orders"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def location(self):
        location_models = (Room, Asset, Building)

        for field in self._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                value = getattr(self, field.name, None)
                if value and isinstance(value, location_models):
                    label = value.__class__.__name__
                    return f"{label}: {value}"
        return "General"

    def log(self, user, action, notes=""):
        History.objects.create(
            content_object=self,
            user=user,
            action=action,
            notes=notes
        )

    def clean(self):
        if not any([self.building, self.room, self.asset]):
            raise ValidationError("A work order must reference a building, room, or asset.")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class WorkOrderComment(models.Model):
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Comment by {self.user} on {self.timestamp}"


class Inspection(models.Model):
    title = models.CharField(max_length=255)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_inspections"
    )
    building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspections_for_building"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspections_for_room"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspections_for_asset"
    )
    scheduled_for = models.DateField()
    performed_at = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=InspectionStatus,
        default=InspectionStatus.SCHEDULED
    )
    findings = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.title} – {self.get_status_display()}"
