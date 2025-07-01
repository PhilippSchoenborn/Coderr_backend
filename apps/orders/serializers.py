from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. Includes nested user and offer data for frontend compatibility.
    """
    user = serializers.SerializerMethodField()
    offer = serializers.SerializerMethodField()
    offer_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'offer', 'offer_detail', 'created_at', 'status']
    
    def get_user(self, obj):
        """Return user data with profile information."""
        if obj.user and hasattr(obj.user, 'profile'):
            profile = obj.user.profile
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'email': obj.user.email,
                'profile': {
                    'id': profile.id,
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'location': profile.location,
                    'tel': profile.tel,
                    'description': profile.description,
                    'type': profile.type,
                    'file': profile.file.url if profile.file else None
                }
            }
        return {
            'id': obj.user.id if obj.user else None,
            'username': obj.user.username if obj.user else None,
            'first_name': obj.user.first_name if obj.user else None,
            'last_name': obj.user.last_name if obj.user else None,
            'email': obj.user.email if obj.user else None,
            'profile': None
        }
    
    def get_offer(self, obj):
        """Return basic offer data."""
        if obj.offer:
            return {
                'id': obj.offer.id,
                'title': obj.offer.title,
                'description': obj.offer.description,
                'image': obj.offer.file.url if obj.offer.file else None,
                'created_at': obj.offer.created_at,
                'updated_at': obj.offer.updated_at
            }
        return None
    
    def get_offer_detail(self, obj):
        """Return offer detail data if available."""
        if obj.offer_detail:
            return {
                'id': obj.offer_detail.id,
                'title': obj.offer_detail.title,
                'price': float(obj.offer_detail.price) if obj.offer_detail.price else None,
                'delivery_time_in_days': obj.offer_detail.delivery_time_in_days,
                'revisions': obj.offer_detail.revisions,
                'features': obj.offer_detail.features,
                'offer_type': obj.offer_detail.offer_type
            }
        return None
