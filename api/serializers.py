from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Offer
from rest_framework.authtoken.models import Token
import base64
from django.core.files.base import ContentFile

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

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True, required=True)
    type = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )
        Profile.objects.create(
            user=user,
            username=user.username,
            type=validated_data['type'],
            email=user.email
        )
        Token.objects.get_or_create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class OfferSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(source='owner', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    image_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'price', 'image', 'image_base64', 'created_at', 'updated_at', 'owner', 'user']
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True},
            'image_base64': {'required': False},
            'price': {'required': False, 'allow_null': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('image') is None:
            data['image'] = ''
        # Dummy-Details für Kompatibilität mit Frontend
        if 'details' not in data or not isinstance(data['details'], list) or len(data['details']) == 0:
            offer_id = data.get('id', 0)
            data['details'] = [
                {
                    'id': int(f"{offer_id}1"),
                    'title': 'Basic Paket',
                    'revisions': 2,
                    'delivery_time_in_days': 3,
                    'price': 49.99,
                    'features': ['1x Beratung', 'E-Mail Support'],
                    'offer_type': 'basic',
                },
                {
                    'id': int(f"{offer_id}2"),
                    'title': 'Standard Paket',
                    'revisions': 3,
                    'delivery_time_in_days': 2,
                    'price': 79.99,
                    'features': ['2x Beratung', 'Telefon Support'],
                    'offer_type': 'standard',
                },
                {
                    'id': int(f"{offer_id}3"),
                    'title': 'Premium Paket',
                    'revisions': 5,
                    'delivery_time_in_days': 1,
                    'price': 129.99,
                    'features': ['Unbegrenzte Beratung', 'Premium Support'],
                    'offer_type': 'premium',
                },
            ]
        data.pop('image_base64', None)
        return data

    def validate_price(self, value):
        # Preis ist optional, validiere nur wenn vorhanden
        if value in (None, ''):
            return None
        from decimal import Decimal, InvalidOperation
        try:
            return Decimal(str(value).replace(',', '.'))
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError('Ungültiger Preis.')

    def create(self, validated_data):
        image_base64 = validated_data.pop('image_base64', None)
        image = validated_data.pop('image', None)
        # Setze den aktuellen User als owner
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            validated_data['owner'] = request.user
        offer = Offer.objects.create(**validated_data)
        if image:
            offer.image = image
            offer.save()
        elif image_base64:
            format, imgstr = image_base64.split(';base64,') if ';base64,' in image_base64 else (None, image_base64)
            ext = format.split('/')[-1] if format else 'png'
            file_name = f"offer_{offer.id}.{ext}"
            offer.image = ContentFile(base64.b64decode(imgstr), name=file_name)
            offer.save()
        return offer

    def update(self, instance, validated_data):
        image_base64 = validated_data.pop('image_base64', None)
        image = validated_data.pop('image', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if image is not None:
            instance.image = image
        elif image_base64:
            format, imgstr = image_base64.split(';base64,') if ';base64,' in image_base64 else (None, image_base64)
            ext = format.split('/')[-1] if format else 'png'
            file_name = f"offer_{instance.id}.{ext}"
            instance.image = ContentFile(base64.b64decode(imgstr), name=file_name)
        instance.save()
        return instance
