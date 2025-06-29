from rest_framework import serializers
from .models import Offer, OfferDetail
from django.db.models import Min

class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for OfferDetail model, representing a single offer package (basic/standard/premium)."""
    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type'
        ]

class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer model, including details and computed fields for min price/time."""
    details = OfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_min_price(self, obj):
        """Return the minimum price among all offer details."""
        prices = [d.price for d in obj.details.all() if d.price is not None]
        return float(min(prices)) if prices else None

    def get_min_delivery_time(self, obj):
        """Return the minimum delivery time among all offer details."""
        times = [d.delivery_time_in_days for d in obj.details.all() if d.delivery_time_in_days is not None]
        return int(min(times)) if times else None

    def get_image(self, obj):
        """Return the image URL if available."""
        return obj.image.url if hasattr(obj, 'image') and obj.image else None

    def get_user(self, obj):
        """Return the owner's user ID."""
        return obj.owner.id if obj.owner else None

    def get_user_details(self, obj):
        """Return basic profile info of the offer owner."""
        if obj.owner and hasattr(obj.owner, 'profile'):
            profile = obj.owner.profile
            return {
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'username': profile.username or ''
            }
        return None
