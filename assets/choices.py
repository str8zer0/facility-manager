from django.db import models


class StatusCode(models.TextChoices):
    OPERATIONAL = "101", "Operational"
    OUT_OF_ORDER = "301", "Out of order"
    MAINTENANCE = "501", "Maintenance"
    FOR_REPAIR = "502", "For repair"
    AWAITING_SPARE_PART = "202", "Awaiting maintenance"
    AWAITING_REPAIR = "201", "Awaiting repair"
