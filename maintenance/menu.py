from common.menu_registry import menu_registry

menu_registry.register({
    "label": "Maintenance",
    "icon": "fas fa-tools",
    "roles": ["admin", "manager", "technician", "staff"],
    "items": [
            {
                "label": "Work Orders",
                "url": "maintenance:workorder_list",
                "icon": "fas fa-clipboard-list",
                "roles": ["admin", "manager", "technician", "staff"],
            },
            {
                "label": "Inspections",
                "url": "maintenance:inspection_list",
                "icon": "fas fa-clipboard-check",
                "roles": ["admin", "manager", "technician"],
            },
        ]
    }
)