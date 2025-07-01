"""
Business logic helpers for offers app.
Separates validation and creation logic from views.
"""
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from .models import Offer, OfferDetail
from apps.profiles.models import Profile


class OfferBusinessLogic:
    """Business logic for offer operations"""
    
    @staticmethod
    def validate_user_permissions(user):
        """Validate that user can create offers"""
        if not user or not user.is_authenticated:
            return Response(
                {'detail': 'Authentifizierung erforderlich.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Kein Profil gefunden.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if profile.type != 'business':
            return Response(
                {'detail': 'Nur Business-Profile dürfen Angebote erstellen.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return None  # No error
    
    @staticmethod
    def validate_offer_data(data):
        """Validate offer creation data"""
        # Title validation
        if not data.get('title') or not isinstance(data.get('title'), str) or not data['title'].strip():
            return Response(
                {'detail': 'Titel muss angegeben werden.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Description validation
        if not data.get('description') or not isinstance(data.get('description'), str) or not data['description'].strip():
            return Response(
                {'detail': 'Beschreibung muss angegeben werden.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Details validation
        details_data = data.get('details')
        if not details_data or not isinstance(details_data, list) or len(details_data) != 3:
            return Response(
                {'detail': 'Es müssen genau 3 Angebotsdetails übergeben werden.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate each detail
        for detail in details_data:
            required_fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
            for field in required_fields:
                if field not in detail or detail[field] in [None, '', []]:
                    return Response(
                        {'detail': f'Feld "{field}" in Angebotsdetails fehlt oder ist leer.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return None  # No error
    
    @staticmethod
    def create_offer_with_details(user, data):
        """Create offer and its details"""
        try:
            # Create offer
            offer = Offer.objects.create(
                owner=user,
                title=data.get('title'),
                file=data.get('image'),
                description=data.get('description'),
            )
            
            # Create details
            details_objs = []
            for detail in data.get('details', []):
                od = OfferDetail.objects.create(
                    offer=offer,
                    title=detail['title'],
                    revisions=detail['revisions'],
                    delivery_time_in_days=detail['delivery_time_in_days'],
                    price=detail['price'],
                    features=detail['features'],
                    offer_type=detail['offer_type'],
                )
                details_objs.append(od)
            
            return offer, details_objs
        
        except Exception as e:
            raise Exception(f"Error creating offer: {str(e)}")
    
    @staticmethod
    def format_offer_response(offer, details_objs):
        """Format offer response data"""
        return {
            'id': offer.id,
            'title': offer.title,
            'image': offer.file.url if offer.file else None,
            'description': offer.description,
            'details': [
                {
                    'id': d.id,
                    'title': d.title,
                    'revisions': d.revisions,
                    'delivery_time_in_days': d.delivery_time_in_days,
                    'price': d.price,
                    'features': d.features,
                    'offer_type': d.offer_type,
                } for d in details_objs
            ]
        }
