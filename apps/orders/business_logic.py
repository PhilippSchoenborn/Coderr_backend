"""
Business logic for orders app.
Extracts business logic from views to separate concerns.
"""
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from apps.profiles.models import Profile
from apps.offers.models import OfferDetail


class OrderBusinessLogic:
    """Business logic for order operations."""
    
    @staticmethod
    def get_order_count_for_business(business_user_id, order_status='in_progress'):
        """Get count of orders for a business user with specific status."""
        try:
            business_profile = Profile.objects.get(user_id=business_user_id, type='business')
        except Profile.DoesNotExist:
            return None, "Business user not found."
        
        order_count = Order.objects.filter(
            offer__owner=business_user_id, 
            status=order_status
        ).count()
        return order_count, None
    
    @staticmethod
    def validate_customer_profile(user):
        """Validate that user has a customer profile."""
        try:
            profile = Profile.objects.get(user=user)
            if profile.type != 'customer':
                return None, "Nur Kunden dürfen Bestellungen anlegen."
            return profile, None
        except Profile.DoesNotExist:
            return None, "Kein Profil gefunden."
    
    @staticmethod
    def validate_offer_detail_id(offer_detail_id):
        """Validate and return offer detail."""
        if not offer_detail_id:
            return None, "offer_detail_id muss angegeben werden."
        
        try:
            offer_detail_id_int = int(offer_detail_id)
        except (ValueError, TypeError):
            return None, "offer_detail_id muss eine Zahl sein."
        
        try:
            offer_detail = OfferDetail.objects.get(pk=offer_detail_id_int)
        except OfferDetail.DoesNotExist:
            return None, "Angebotsdetail nicht gefunden."
        
        return offer_detail, None
    
    @staticmethod
    def create_order(user, offer_detail):
        """Create a new order."""
        offer = offer_detail.offer
        if not offer:
            return None, "Kein zugehöriges Angebot gefunden."
        
        try:
            order = Order.objects.create(
                user=user,
                offer=offer,
                offer_detail=offer_detail,
                status='in_progress',
            )
            return order, None
        except Exception:
            return None, "Interner Serverfehler."
    
    @staticmethod
    def check_order_access_permission(user, order):
        """Check if user has permission to access the order."""
        # Order owner or business owner can access
        if user == order.user:
            return True
        if hasattr(order, 'offer') and user == order.offer.owner:
            return True
        return False
