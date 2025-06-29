from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. Serializes all fields of the Order instance for API usage.
    """
    class Meta:
        model = Order
        fields = '__all__'
        # All fields of the Order model are included in the serialization.
