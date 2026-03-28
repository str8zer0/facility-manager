from django.db import models
from accounts.models import User
from common.models import History
from facilities.models import Room
from assets.choices import TagName, StatusCode


class AssetCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Asset(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        "AssetCategory",
        on_delete=models.SET_NULL,
        null=True,
        related_name="assets"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets"
    )
    tag = models.CharField(max_length=50, choices=TagName, null=True, blank=True)
    status = models.CharField(max_length=50, choices=StatusCode, default=StatusCode.OPERATIONAL)
    serial_number = models.CharField(max_length=255, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    model_number = models.CharField(max_length=255, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    warranty_expiration = models.DateField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_assets"
    )

    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["category__name", "name"]

    def log(self, user, action, notes=""):
        History.objects.create(
            content_object=self,
            user=user,
            action=action,
            notes=notes
        )

    def __str__(self):
        return self.name
