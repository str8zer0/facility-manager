from common.menu_registry import menu_registry

menu_registry.register({
    "label": "Inventory",
    "icon": "fas fa-warehouse",
    "roles": ["admin", "manager", "technician"],
    "items": [
            {
                "label": "Spare Parts",
                "url": "inventory:sparepart_list",
                "icon": "fas fa-cogs",
                "roles": ["admin", "manager", "technician"],
            },
            {
                "label": "Suppliers",
                "url": "inventory:supplier_list",
                "icon": "fas fa-truck",
                "roles": ["admin", "manager", "technician"],
            },
            {
                "label": "Movements",
                "url": "inventory:movement_list",
                "icon": "fas fa-exchange-alt",
                "roles": ["admin", "manager", "technician"],
            },
        ]
    }
)