from rest_framework import permissions


class IsOrderRelatedUser(permissions.BasePermission):
    """
    Custom permission to only allow users related to an order to view it.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has object permission."""
        # User is either the customer or the business owner
        return obj.customer == request.user or obj.offer_detail.offer.owner == request.user


class IsBusinessOwner(permissions.BasePermission):
    """
    Custom permission to only allow business owners of an order to modify it.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has object permission."""
        # User is the business owner of the offer
        return obj.offer_detail.offer.owner == request.user


class IsAdminOrOrderRelatedUser(permissions.BasePermission):
    """
    Custom permission to allow admins or users related to an order to access it.
    For DELETE operations, only admins are allowed.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has object permission."""
        # For DELETE operations, only admins can delete orders
        if request.method == 'DELETE':
            return request.user.is_staff or request.user.is_superuser
        
        # For other operations, admins can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # User is either the customer or the business owner
        return obj.customer == request.user or obj.offer_detail.offer.owner == request.user


class IsAdminOrBusinessOwner(permissions.BasePermission):
    """
    Custom permission to allow admins or business owners to modify orders.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has object permission."""
        # Admins can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # User is the business owner of the offer
        return obj.offer_detail.offer.owner == request.user
