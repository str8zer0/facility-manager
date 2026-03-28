from django.contrib import admin
from maintenance.models import WorkOrderComment, WorkOrderAttachment, InspectionItem, InspectionResult


class WorkOrderCommentInline(admin.TabularInline):
    model = WorkOrderComment
    extra = 0
    readonly_fields = ("timestamp",)


class WorkOrderAttachmentInline(admin.TabularInline):
    model = WorkOrderAttachment
    extra = 0
    readonly_fields = ("uploaded_at",)


class InspectionItemInline(admin.TabularInline):
    model = InspectionItem
    extra = 1


class InspectionResultInline(admin.TabularInline):
    model = InspectionResult
    extra = 0
    readonly_fields = ("photo",)
