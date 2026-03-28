from django.db import models
from inventory.choices import Reason
from maintenance.models import WorkOrder


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class SparePart(models.Model):
    name = models.CharField(max_length=255)
    part_number = models.CharField(max_length=255, blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="spare_parts"
    )
    quantity = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.part_number})"


class StockMovement(models.Model):
    part = models.ForeignKey(
        SparePart,
        on_delete=models.CASCADE,
        related_name="movements_for_part"
    )
    change = models.IntegerField()   # negative or positive
    reason = models.CharField(max_length=50, choices=Reason)
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movements_for_work_order"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.change} x {self.part.name} ({self.reason})"
