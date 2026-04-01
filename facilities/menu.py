from common.menu_registry import menu_registry

menu_registry.register({
    "label": "Facilities",
    "icon": "fas fa-building",
    "roles": ["admin", "manager", "technician", "staff"],
    "items": [
            {
                "label": "Buildings",
                "url": "facilities:building_list",
                "icon": "fas fa-city",
                "roles": ["admin", "manager", "technician", "staff"],
            },
            {
                "label": "Rooms",
                "url": "facilities:room_list",
                "icon": "fas fa-door-open",
                "roles": ["admin", "manager", "technician", "staff"],
            },
        ]
    }
)
