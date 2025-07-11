from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to modify object."""
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to read/edit it.
    Restricts ALL access (including GET) to the owner only.
    """

    def has_object_permission(self, request, view, obj):
        """Check if user is the owner of the object."""
        return obj.owner == request.user


class IsBusinessUser(permissions.BasePermission):
    """
    Custom permission to only allow business users to create offers.
    Returns 403 for customer users.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated business user."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has a business profile
        try:
            return request.user.profile.type == 'business'
        except AttributeError:
            return False


class IsCustomerUser(permissions.BasePermission):
    """
    Custom permission to only allow customer users to place orders.
    Returns 403 for business users.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated customer user."""
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has a customer profile
        try:
            return request.user.profile.type == 'customer'
        except AttributeError:
            return False
