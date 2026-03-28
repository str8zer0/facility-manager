from django.contrib.contenttypes.admin import GenericTabularInline
from common.models import History


class HistoryInline(GenericTabularInline):
    model = History
    extra = 0
    readonly_fields = ("timestamp", "user", "action", "notes")