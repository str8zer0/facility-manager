from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrReadOnly(BasePermission):
    """
    Read access: any authenticated user.
    Write access (POST, PUT, PATCH, DELETE): Manager or Admin only.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_superuser or
                request.user.groups.filter(name__in=["Manager", "Admin"]).exists()
            )
        )


class IsOwnerOrManager(BasePermission):
    """
    Read access: any authenticated user.
    Create access: any authenticated user.
    Update/Delete access: the creator or a Manager/Admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name__in=["Manager", "Admin"]).exists():
            return True

        # Allow the creator to edit/delete their own work orders
        return getattr(obj, "created_by", None) == request.user