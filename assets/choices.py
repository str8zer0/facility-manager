from django.db import models


class TagName(models.TextChoices):
    POWER_DISTRIBUTION = "POWER_DISTRIBUTION", "Power Distribution"
    LIGHTING = "LIGHTING", "Lighting"
    WATER_SUPPLY = "WATER_SUPPLY", "Water Supply"
    DRAINAGE = "DRAINAGE", "Drainage"
    VENTILATION = "VENTILATION", "Ventilation"
    HEATING = "HEATING", "Heating"
    COOLING = "COOLING", "Cooling"
    AIR_QUALITY = "AIR_QUALITY", "Air Quality"

    FIRE_SUPPRESSION = "FIRE_SUPPRESSION", "Fire Suppression"
    FIRE_DETECTION = "FIRE_DETECTION", "Fire Detection"
    SECURITY_MONITORING = "SECURITY_MONITORING", "Security Monitoring"
    ACCESS_CONTROL = "ACCESS_CONTROL", "Access Control"
    EMERGENCY_LIGHTING = "EMERGENCY_LIGHTING", "Emergency Lighting"

    PRODUCTION_EQUIPMENT = "PRODUCTION_EQUIPMENT", "Production Equipment"
    WORKSHOP_TOOL = "WORKSHOP_TOOL", "Workshop Tool"
    TRANSPORT_EQUIPMENT = "TRANSPORT_EQUIPMENT", "Transport Equipment"
    STORAGE_EQUIPMENT = "STORAGE_EQUIPMENT", "Storage Equipment"

    NETWORK_INFRASTRUCTURE = "NETWORK_INFRASTRUCTURE", "Network Infrastructure"
    SERVER_EQUIPMENT = "SERVER_EQUIPMENT", "Server Equipment"
    COMMUNICATION_SYSTEM = "COMMUNICATION_SYSTEM", "Communication System"

    CLEANING_EQUIPMENT = "CLEANING_EQUIPMENT", "Cleaning Equipment"
    WASTE_MANAGEMENT = "WASTE_MANAGEMENT", "Waste Management"
    KITCHEN_APPLIANCE = "KITCHEN_APPLIANCE", "Kitchen Appliance"


class StatusCode(models.TextChoices):
    OPERATIONAL = "101", "Operational"
    OUT_OF_ORDER = "301", "Out of order"
    MAINTENANCE = "501", "Maintenance"
    FOR_REPAIR = "502", "For repair"
    AWAITING_SPARE_PART = "202", "Awaiting maintenance"
    AWAITING_REPAIR = "201", "Awaiting repair"
