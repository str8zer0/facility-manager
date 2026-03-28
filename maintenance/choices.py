from django.db import models

class WorkOrderStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    ON_HOLD = "ON_HOLD", "On Hold"
    AWAITING_PARTS = "AWAITING_PARTS", "Awaiting Parts"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class WorkOrderPriority(models.TextChoices):
    LOW = "1", "Low"
    MEDIUM = "2", "Medium"
    HIGH = "3", "High"
    CRITICAL = "4", "Critical"


class ResultStatus(models.TextChoices):
    PASS = "PASS", "Pass"
    FAIL = "FAIL", "Fail"
    NA = "NA", "Not Applicable"


class InspectionStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
