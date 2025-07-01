from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Return True if request is safe or user is owner."""
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
