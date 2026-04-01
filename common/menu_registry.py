class MenuRegistry:

    def __init__(self):
        self._menus = []

    def register(self, *menus):
        self._menus.extend(menus)

    def get_for_role(self, role):
        visible_menus = []

        for menu in self._menus:
            if role not in menu["roles"]:
                continue

            items = [
                item for item in menu["items"]
                if role in item["roles"]
            ]

            if not items:
                continue

            visible_menus.append({**menu, "items": items})

        return visible_menus


# Global instance
menu_registry = MenuRegistry()

