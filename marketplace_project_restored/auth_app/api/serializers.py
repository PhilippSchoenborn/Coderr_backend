from rest_framework import serializers
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with profile creation.
    
    Handles user account creation and automatically creates
    an associated profile with the specified type (customer/business).
    """
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=['customer', 'business'], write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeated_password', 'type')

    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return value

    def validate_username(self, value):
        """Validate that username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        """
        Create user and associated profile.
        
        Args:
            validated_data: Validated serializer data
            
        Returns:
            User: Created user instance with associated profile
        """
        from profiles_app.models import Profile
        
        profile_type = validated_data.pop('type')
        validated_data.pop('repeated_password')
        
        user = self._create_user(validated_data)
        self._create_profile(user, profile_type)
        return user

    def _create_user(self, validated_data):
        """Create user instance."""
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

    def _create_profile(self, user, profile_type):
        """Create profile for user."""
        from profiles_app.models import Profile
        Profile.objects.create(user=user, type=profile_type)


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    
    Accepts username/email and password for login.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
