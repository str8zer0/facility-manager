from django.contrib import admin
from common.models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("content_object", "action", "user", "timestamp")
    list_filter = ("content_type", "timestamp", "user")
    search_fields = ("action", "notes")
    readonly_fields = ("timestamp",)
