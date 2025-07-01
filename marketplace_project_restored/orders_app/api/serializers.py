from rest_framework import serializers
from ..models import Order
from offers_app.models import OfferDetail
from offers_app.api.serializers import OfferDetailSerializer


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model.
    """
    customer_user = serializers.SerializerMethodField()
    offer_detail = OfferDetailSerializer(read_only=True)
    business_user = serializers.SerializerMethodField()
    
    # Flattened fields from offer_detail
    title = serializers.SerializerMethodField()
    revisions = serializers.SerializerMethodField()
    delivery_time_in_days = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    offer_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'offer_detail', 'business_user', 'title', 'revisions', 
                 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 
                           'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']

    def get_customer_user(self, obj):
        """Return the customer's ID as 'customer_user' field."""
        return obj.customer.id

    def get_business_user(self, obj):
        """Return the business user's ID as 'business_user' field."""
        return obj.business_user.id

    def get_title(self, obj):
        """Return the offer detail title."""
        return obj.offer_detail.title

    def get_revisions(self, obj):
        """Return the offer detail revisions."""
        return obj.offer_detail.revisions

    def get_delivery_time_in_days(self, obj):
        """Return the offer detail delivery time."""
        return obj.offer_detail.delivery_time_in_days

    def get_price(self, obj):
        """Return the offer detail price."""
        return obj.offer_detail.price

    def get_features(self, obj):
        """Return the offer detail features."""
        return obj.offer_detail.features

    def get_offer_type(self, obj):
        """Return the offer detail type."""
        return obj.offer_detail.offer_type


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Order.
    """
    offer_detail_id = serializers.IntegerField()
    
    class Meta:
        model = Order
        fields = ['offer_detail_id']
    
    def validate_offer_detail_id(self, value):
        """Validate offer detail ID."""
        try:
            offer_detail = OfferDetail.objects.get(id=value)
            return value
        except OfferDetail.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Offer detail not found.")
    
    def create(self, validated_data):
        """Create new order."""
        offer_detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])
        
        # Check if customer is trying to order their own service
        if offer_detail.offer.owner == self.context['request'].user:
            raise serializers.ValidationError("You cannot order your own service.")
        
        return Order.objects.create(
            customer=self.context['request'].user,
            offer_detail=offer_detail
        )


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating order status.
    """
    class Meta:
        model = Order
        fields = ['status']
