from rest_framework import serializers
from ..models import Review
from django.contrib.auth.models import User


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    """
    reviewer = serializers.SerializerMethodField()
    business_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'business_user', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'business_user', 'created_at', 'updated_at']
    
    def get_reviewer(self, obj):
        """Return the reviewer's ID."""
        return obj.reviewer.id
    
    def get_business_user(self, obj):
        """Return the business user's ID."""
        return obj.business_user.id


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Review.
    """
    business_user = serializers.IntegerField()
    
    class Meta:
        model = Review
        fields = ['business_user', 'rating', 'description']
    
    def validate_business_user(self, value):
        """Validate business user."""
        try:
            user = User.objects.get(id=value)
            if not hasattr(user, 'profile') or user.profile.type != 'business':
                raise serializers.ValidationError("User is not a business user.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Business user not found.")
    
    def validate(self, data):
        """Validate review data."""
        business_user = User.objects.get(id=data['business_user'])
        reviewer = self.context['request'].user
        
        # Check if reviewer is trying to review themselves
        if business_user == reviewer:
            raise serializers.ValidationError("You cannot review yourself.")
        
        # Check if review already exists
        if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
            raise serializers.ValidationError("You have already reviewed this business user.")
        
        return data
    
    def create(self, validated_data):
        """Create new review."""
        business_user = User.objects.get(id=validated_data.pop('business_user'))
        return Review.objects.create(
            reviewer=self.context['request'].user,
            business_user=business_user,
            **validated_data
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Review.
    """
    class Meta:
        model = Review
        fields = ['rating', 'description']
