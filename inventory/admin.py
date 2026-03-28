from django.contrib import admin
from inventory.inlines import StockMovementInline
from inventory.models import Supplier, SparePart, StockMovement


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone")
    search_fields = ("name", "contact_email")


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    inlines = [StockMovementInline]

    list_display = ("name", "part_number", "supplier", "quantity", "minimum_quantity")
    list_filter = ("supplier",)
    search_fields = ("name", "part_number")
    autocomplete_fields = ("supplier",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("part", "change", "reason", "work_order", "timestamp")
    list_filter = ("reason", "timestamp")
    search_fields = ("part__name",)
    autocomplete_fields = ("part", "work_order")
    readonly_fields = ("timestamp",)
