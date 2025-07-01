from rest_framework import serializers
from ..models import Profile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    Handles validation and serialization of user profile data including
    custom validation for email, names, and other profile fields.
    Enforces required fields and read-only field restrictions.
    """
    user = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
            'updated_at',
            'uploaded_at']
        read_only_fields = [
            'id',
            'user',
            'type',
            'created_at',
            'updated_at',
            'username',
            'email',
            'uploaded_at']

    def get_user(self, obj):
        """Return the user ID instead of the full user object."""
        return obj.user.id

    def validate_first_name(self, value):
        """
        Validate first name is not empty and not only digits.
        """
        if value and not value.strip():
            raise serializers.ValidationError('First name cannot be empty.')
        if value and value.isdigit():
            raise serializers.ValidationError(
                'First name cannot consist only of digits.')
        return value

    def validate_last_name(self, value):
        """
        Validate last name is not empty and not only digits.
        """
        if value and not value.strip():
            raise serializers.ValidationError('Last name cannot be empty.')
        if value and value.isdigit():
            raise serializers.ValidationError(
                'Last name cannot consist only of digits.')
        return value

    def validate_description(self, value):
        """
        Validate description has minimum length if provided.
        """
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError(
                'Description must be at least 5 characters long.')
        return value

    def validate_location(self, value):
        """
        Validate location has minimum length if provided.
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                'Location must be at least 2 characters long.')
        return value

    def validate_working_hours(self, value):
        """
        Validate working hours has minimum length if provided.
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                'Working hours must be at least 2 characters long.')
        return value

    def to_representation(self, instance):
        """
        Convert model instance to serialized representation.

        Ensures string fields are never null but empty strings if no value present.
        """
        data = super().to_representation(instance)
        return self._ensure_string_fields_not_null(data)

    def _ensure_string_fields_not_null(self, data):
        """Ensure string fields are empty strings instead of null."""
        string_fields = [
            'first_name',
            'last_name',
            'location',
            'tel',
            'description',
            'working_hours']

        for field in string_fields:
            if data.get(field) is None:
                data[field] = ''

        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Profile.
    """
    email = serializers.EmailField(required=False)

    class Meta:
        model = Profile
        fields = [
            'file',
            'first_name',
            'last_name',
            'location',
            'tel',
            'description',
            'working_hours',
            'email']

    def validate_first_name(self, value):
        """Validate first name."""
        if value and not value.strip():
            raise serializers.ValidationError('First name cannot be empty.')
        if value and value.isdigit():
            raise serializers.ValidationError(
                'First name cannot consist only of digits.')
        return value

    def validate_last_name(self, value):
        """Validate last name."""
        if value and not value.strip():
            raise serializers.ValidationError('Last name cannot be empty.')
        if value and value.isdigit():
            raise serializers.ValidationError(
                'Last name cannot consist only of digits.')
        return value

    def update(self, instance, validated_data):
        """Update profile and user email."""
        email = validated_data.pop('email', None)

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update user email if provided
        if email:
            instance.user.email = email
            instance.user.save()

        return instance
