from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Allow read-only access for any request, otherwise enforce ownership or admin."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.role == "admin"


