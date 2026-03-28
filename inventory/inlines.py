from django.contrib import admin
from inventory.models import StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ("timestamp",)
