from django.db import models
from accounts.models import User


class Building(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_buildings"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=255)
    floor = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="rooms"
    )

    class Meta:
        unique_together = ("building", "name")
        ordering = ["building__name", "name"]

    def __str__(self):
        return f"{self.building.name} – {self.name}"
