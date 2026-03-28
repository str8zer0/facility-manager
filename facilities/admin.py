from django.contrib import admin
from .models import Building, Room


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "manager")
    search_fields = ("name", "address", "manager__email")
    ordering = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "floor")
    list_filter = ("building", "floor")
    search_fields = ("name", "building__name")
    ordering = ("building__name", "name")
