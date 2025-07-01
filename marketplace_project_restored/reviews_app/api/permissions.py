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
    Returns 401 for business users as if they were not authenticated.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For business users, act as if they're not authenticated (401)
        if hasattr(request.user, 'profile') and request.user.profile.type == 'business':
            # Raise authentication error instead of permission error
            from rest_framework.exceptions import NotAuthenticated
            raise NotAuthenticated("Authentication credentials were not provided.")
            
        # Only customer users can create reviews
        return hasattr(request.user, 'profile') and request.user.profile.type == 'customer'
