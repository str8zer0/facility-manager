from django.contrib import admin
from common.inlines import HistoryInline
from maintenance.inlines import WorkOrderCommentInline, WorkOrderAttachmentInline, \
    InspectionItemInline, InspectionResultInline
from maintenance.models import WorkOrder, InspectionTemplate, Inspection


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    inlines = [WorkOrderCommentInline, WorkOrderAttachmentInline, HistoryInline]

    list_display = ("title", "status", "priority", "created_by", "created_at", "due_date", "location")
    list_filter = ("status", "priority", "created_at", "due_date")
    search_fields = ("title", "description")
    autocomplete_fields = ("asset", "room", "building", "created_by", "assigned_to")
    readonly_fields = ("created_at", "updated_at")


@admin.register(InspectionTemplate)
class InspectionTemplateAdmin(admin.ModelAdmin):
    inlines = [InspectionItemInline]

    list_display = ("name", "is_active", "created_by", "created_at")
    search_fields = ("name",)


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    inlines = [InspectionResultInline]

    list_display = ("template", "status", "performed_by", "scheduled_for", "performed_at", "asset", "room", "building")
    list_filter = ("status", "scheduled_for", "performed_at", "template")
    search_fields = ("notes",)
    autocomplete_fields = ("template", "performed_by", "asset", "room", "building")
    readonly_fields = ("timestamp",)
