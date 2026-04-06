from django.contrib import admin
from common.inlines import HistoryInline
from assets.models import AssetCategory, Asset


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_categories",
        "room",
        "status_display",
        "is_active",
        "assigned_to",
    )
    list_filter = (
        "categories",
        "status",
        "is_active",
        "room__building",
        "room",
    )
    search_fields = (
        "name",
        "serial_number",
        "manufacturer",
        "model_number",
        "assigned_to__email",
    )
    autocomplete_fields = ("room", "assigned_to")
    inlines = [HistoryInline]
    ordering = ("name",)

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = "Categories"

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = "Status"