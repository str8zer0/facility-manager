from django.contrib import admin
from common.inlines import HistoryInline
from maintenance.inlines import WorkOrderCommentInline
from maintenance.models import WorkOrder, Inspection


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    inlines = [WorkOrderCommentInline, HistoryInline]

    list_display = ("title", "status", "priority", "created_by", "created_at", "due_date", "location")
    list_filter = ("status", "priority", "created_at", "due_date")
    search_fields = ("title", "description")
    autocomplete_fields = ("asset", "room", "building", "created_by", "assigned_to")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):

    list_display = ("title", "status", "performed_by", "scheduled_for", "performed_at", "asset", "room", "building")
    list_filter = ("status", "scheduled_for", "performed_at")
    search_fields = ("findings",)
    autocomplete_fields = ("performed_by", "asset", "room", "building")
    readonly_fields = ("timestamp",)
