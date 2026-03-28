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
    assigned_to = models.ManyToManyField(
        User,
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
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Comment by {self.user} on {self.timestamp}"


class WorkOrderAttachment(models.Model):
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(upload_to="workorder_attachments/")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.work_order}"


class InspectionTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_inspection_templates"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InspectionItem(models.Model):
    template = models.ForeignKey(
        InspectionTemplate,
        on_delete=models.CASCADE,
        related_name="items"
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.template.name} – {self.text}"


class Inspection(models.Model):
    template = models.ForeignKey(
        InspectionTemplate,
        on_delete=models.PROTECT,
        related_name="inspections"
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
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
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.template.name} – {self.timestamp}"


class InspectionResult(models.Model):
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name="results_for_inspection"
    )
    item = models.ForeignKey(
        InspectionItem,
        on_delete=models.CASCADE,
        related_name="results_for_item"
    )
    status = models.CharField(
        max_length=10,
        choices=ResultStatus,
        default=ResultStatus.NA
    )
    notes = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to="inspection_photos/",
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("inspection", "item")
        ordering = ["item__order"]

    def __str__(self):
        return f"{self.item.text} – {self.status}"
