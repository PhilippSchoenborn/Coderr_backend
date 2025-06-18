from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

class SuperUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_superuser = serializers.BooleanField(default=True, read_only=True)
    is_staff = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'is_superuser',
            'is_staff',
        ]

    def create(self, validated_data):
        user = User.objects.create_superuser(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    type = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    file = serializers.CharField(required=False, allow_blank=True, default='')
    location = serializers.CharField(required=False, allow_blank=True, default='')
    tel = serializers.CharField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    working_hours = serializers.CharField(required=False, allow_blank=True, default='')
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'type', 'email', 'created_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Setze leere Strings für None-Felder
        for field in ['first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours']:
            if data.get(field) is None:
                data[field] = ''
        return data
