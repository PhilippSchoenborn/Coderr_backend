from rest_framework import serializers
from ..models import Offer, OfferDetail
from django.contrib.auth.models import User
from django.db import models
import base64
from django.core.files.base import ContentFile


class Base64OrFileImageField(serializers.Field):
    """
    Custom field that accepts either a base64 string or a file upload.
    """

    def to_internal_value(self, data):
        """Process image data from various formats."""
        print(f"DEBUG: Image field received data type: {type(data)}, value: {data}")

        # Handle file upload (from FormData)
        if hasattr(data, 'read'):
            print("DEBUG: Processing as file upload")
            return data

        # Handle base64 string
        if isinstance(data, str) and data.startswith('data:image'):
            print("DEBUG: Processing as base64 string")
            return self._process_base64_image(data)

        return self._handle_empty_or_invalid_data(data)

    def _handle_empty_or_invalid_data(self, data):
        """Handle empty or invalid image data."""
        if not data:
            print("DEBUG: No image data provided")
            return None

        print(f"DEBUG: Invalid image format: {data}")
        raise serializers.ValidationError(
            "Invalid image format. Expected file or base64 string.")

    def _process_base64_image(self, data):
        """Convert base64 string to file."""
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name=f'offer_image.{ext}')

    def to_representation(self, value):
        """Return representation of the object."""
        return None  # We don't need to return the image data


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail model.
    """
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type']
        
    def validate(self, data):
        """Validate offer detail data."""
        # Check if this is an update (has instance) or create
        if self.instance is None:  # Creating new
            if 'offer_type' not in data:
                raise serializers.ValidationError(
                    {"offer_type": "This field is required."}
                )
        else:  # Updating existing
            # For PATCH operations, offer_type should be provided
            request = self.context.get('request')
            if request and request.method == 'PATCH' and 'offer_type' not in data:
                raise serializers.ValidationError(
                    {"offer_type": "This field is required for updates."}
                )
        return data


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for user details in offers.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer model with expected field names.
    """
    user = serializers.SerializerMethodField()
    user_details = UserDetailsSerializer(source='owner', read_only=True)
    details = OfferDetailSerializer(source='offer_details', many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()  # For frontend compatibility

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'user_details',
            'title',
            'file',
            'image',
            'description',
            'details',
            'min_price',
            'min_delivery_time',
            'created_at',
            'updated_at']
        read_only_fields = [
            'id',
            'user',
            'user_details',
            'min_price',
            'min_delivery_time',
            'created_at',
            'updated_at']

    def get_user(self, obj):
        """Return the owner's ID as 'user' field."""
        return obj.owner.id

    def get_image(self, obj):
        """Return the same value as file field for frontend compatibility."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_min_price(self, obj):
        """Return the minimum price from offer details."""
        if obj.offer_details.exists():
            return obj.offer_details.aggregate(
                min_price=models.Min('price'))['min_price']
        return None

    def get_min_delivery_time(self, obj):
        """Return the minimum delivery time from offer details."""
        if obj.offer_details.exists():
            return obj.offer_details.aggregate(
                min_time=models.Min('delivery_time_in_days'))['min_time']
        return None


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Offer with details.
    """
    details = OfferDetailSerializer(many=True, required=True)
    image = Base64OrFileImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Offer
        fields = ['title', 'description', 'image', 'details']

    def validate_details(self, details):
        """Validate that exactly 3 details are provided."""
        if len(details) != 3:
            raise serializers.ValidationError(
                "Exactly 3 offer details (basic, standard, premium) are required.")
        return details

    def create(self, validated_data):
        """Create offer with details."""
        details_data = validated_data.pop('details', [])
        image_data = validated_data.pop('image', None)

        # Handle image (both base64 and file are processed by custom field)
        if image_data:
            validated_data['file'] = image_data

        offer = Offer.objects.create(**validated_data)
        self._create_offer_details(offer, details_data)
        return offer

    def _create_offer_details(self, offer, details_data):
        """Create offer details for the offer."""
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)


class OfferUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Offer.
    Supports both Base64 image strings and file uploads.
    """
    details = OfferDetailSerializer(many=True, required=False)
    image = Base64OrFileImageField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = Offer
        fields = ['title', 'description', 'image', 'details']

    def update(self, instance, validated_data):
        """Update offer with new data."""
        details_data = validated_data.pop('details', [])
        image_data = validated_data.pop('image', None)

        # Handle image upload (both base64 and file are processed by custom field)
        if image_data:
            instance.file = image_data

        self._update_offer_fields(instance, validated_data)
        self._update_offer_details(instance, details_data)
        return instance

    def _update_offer_fields(self, instance, validated_data):
        """Update offer fields and save."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def _update_offer_details(self, instance, details_data):
        """Update offer details."""
        if details_data:
            instance.offer_details.all().delete()
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)
