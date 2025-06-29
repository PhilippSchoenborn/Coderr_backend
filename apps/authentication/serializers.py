from rest_framework import serializers
from django.contrib.auth.models import User
from apps.profiles.models import Profile
from rest_framework.authtoken.models import Token

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login data. Validates username and password for authentication.
    """
    username = serializers.CharField(help_text="Username of the user.")
    password = serializers.CharField(write_only=True, help_text="User's password (write-only).")

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. Handles validation and creation of new User and Profile instances,
    including password confirmation and user type assignment.
    """
    repeated_password = serializers.CharField(write_only=True, required=True)
    type = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """
        Ensure that the password and repeated_password fields match.
        Raise a validation error if they do not.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        """
        Create a new User and associated Profile instance, and generate an auth token.
        """
        return self._create_user(validated_data)

    def _create_user(self, validated_data):
        """
        Internal helper to create the User, Profile, and Token objects from validated data.
        """
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
        )
        Profile.objects.create(
            user=user,
            username=user.username,
            type=validated_data['type'],
            email=user.email
        )
        Token.objects.get_or_create(user=user)
        return user
