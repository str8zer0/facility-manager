from django import template
from common.menu_registry import menu_registry

register = template.Library()

@register.simple_tag
def global_menu(user) -> list:
    if not user.is_authenticated:
        return []

    role = getattr(user, "role", None)
    if role is None:
        return []

    role = role.lower()

    return menu_registry.get_for_role(role)
