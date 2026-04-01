from django.contrib import admin
from maintenance.models import WorkOrderComment


class WorkOrderCommentInline(admin.TabularInline):
    model = WorkOrderComment
    extra = 0
    readonly_fields = ("timestamp",)

