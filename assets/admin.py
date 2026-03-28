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
        "category",
        "room",
        "tag_display",
        "status_display",
        "is_active",
        "assigned_to",
    )
    list_filter = (
        "category",
        "tag",
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
    autocomplete_fields = ("category", "room", "assigned_to")
    inlines = [HistoryInline]
    ordering = ("name",)

    # Display human-readable labels for tag and status
    def tag_display(self, obj):
        return obj.get_tag_display()
    tag_display.short_description = "Tag"

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = "Status"