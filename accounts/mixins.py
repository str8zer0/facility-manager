from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(LoginRequiredMixin):
    """
    Base mixin for role-based access control using Django Groups.
    Subclasses must define `allowed_groups = [...]`.
    """
    allowed_groups = []

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Superuser bypasses all restrictions
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not user.is_authenticated:
            return self.handle_no_permission()

        user_groups = request.user.groups.values_list("name", flat=True)

        if not any(group in user_groups for group in self.allowed_groups):
            raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(GroupRequiredMixin):
    allowed_groups = ["Admin"]


class ManagerRequiredMixin(GroupRequiredMixin):
    allowed_groups = ["Manager", "Admin"]


class TechnicianRequiredMixin(GroupRequiredMixin):
    allowed_groups = ["Technician", "Manager", "Admin"]


class StaffRequiredMixin(GroupRequiredMixin):
    allowed_groups = ["Staff", "Technician", "Manager", "Admin"]
