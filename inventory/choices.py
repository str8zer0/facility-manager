from django.db import models


class Reason(models.TextChoices):
    PURCHASE = "PURCHASE", "Purchase"
    USED_IN_WORK_ORDER = "USED_IN_WORK_ORDER", "Used in Work Order"
    ADJUSTMENT = "ADJUSTMENT", "Adjustment"