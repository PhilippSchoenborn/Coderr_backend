from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a review to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user has object permission."""
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the review.
        return obj.reviewer == request.user


class IsCustomerUser(permissions.BasePermission):
    """
    Custom permission to only allow customer users to create reviews.
    Returns 403 for business users (they are authenticated but not authorized).
    """

    def has_permission(self, request, view):
        """Check if user has permission."""
        if not request.user or not request.user.is_authenticated:
            return False

        # For business users, return False to trigger 403 (Permission Denied)
        if hasattr(request.user, 'profile') and request.user.profile.type == 'business':
            return False

        # Only customer users can create reviews
        return hasattr(
            request.user,
            'profile') and request.user.profile.type == 'customer'
