from common.menu_registry import menu_registry

menu_registry.register({
    "label": "Assets",
    "icon": "fas fa-boxes",
    "roles": ["admin", "manager", "technician", "staff"],
    "items": [
            {
                "label": "All Assets",
                "url": "assets:asset_list",
                "icon": "fas fa-list",
                "roles": ["admin", "manager", "technician", "staff"],
            },
            {
                "label": "Asset Categories",
                "url": "assets:category_list",
                "icon": "fas fa-tags",
                "roles": ["admin", "manager", "technician", "staff"],
            },
        ]
    }
)
