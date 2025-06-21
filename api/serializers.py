from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Offer, Order
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
    file = serializers.ImageField(required=False, allow_null=True)
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

    def update(self, instance, validated_data):
        # User-Felder extrahieren und separat speichern
        user_data = validated_data.pop('user', {})
        if 'username' in user_data:
            instance.user.username = user_data['username']
        if 'email' in user_data:
            instance.user.email = user_data['email']
        instance.user.save()
        # Restliche Profile-Felder wie gewohnt speichern
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

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
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
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
        # Bild-URL korrekt setzen
        if data.get('image') and hasattr(instance, 'image') and instance.image:
            request = self.context.get('request', None)
            if request is not None:
                data['image'] = request.build_absolute_uri(instance.image.url)
            else:
                data['image'] = instance.image.url
        else:
            data['image'] = ''
        # Details: Wenn vorhanden, übernehme sie, sonst Dummy-Details
        details_from_instance = getattr(instance, '_api_details', None)
        if details_from_instance:
            data['details'] = details_from_instance
        if not data.get('details') or not isinstance(data['details'], list) or len(data['details']) == 0:
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
        # Extrahiere für Kompatibilität die wichtigsten Werte aus dem ersten Detail
        if data['details'] and isinstance(data['details'], list):
            first_detail = data['details'][0]
            data['delivery_time_in_days'] = first_detail.get('delivery_time_in_days')
            data['price'] = first_detail.get('price')
        data.pop('image_base64', None)
        # Debug-Ausgabe: Rohdaten des Objekts
        data['__debug__'] = {
            'raw_instance': {
                'id': getattr(instance, 'id', None),
                'title': getattr(instance, 'title', None),
                'description': getattr(instance, 'description', None),
                'image': str(getattr(instance, 'image', None)),
                'price': str(getattr(instance, 'price', None)),
                'created_at': str(getattr(instance, 'created_at', None)),
                'updated_at': str(getattr(instance, 'updated_at', None)),
                # ggf. weitere Felder
            },
            'raw_data': data.copy()
        }
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

    def validate(self, data):
        import json
        details = data.get('details')
        if isinstance(details, str):
            try:
                details = json.loads(details)
                data['details'] = details
            except Exception:
                raise serializers.ValidationError('Details must be a valid JSON array.')
        if details is None and hasattr(self, 'initial_data'):
            details = self.initial_data.get('details')
            if isinstance(details, str):
                try:
                    details = json.loads(details)
                    data['details'] = details
                except Exception:
                    raise serializers.ValidationError('Details must be a valid JSON array.')
        if details is None or not isinstance(details, list) or len(details) < 3:
            raise serializers.ValidationError('An offer must contain at least 3 details.')
        for detail in details:
            if not isinstance(detail, dict):
                raise serializers.ValidationError('Each detail must be an object.')
            # Typprüfung für jedes Feld
            # --- PATCH: Versuche, revisions und delivery_time_in_days in int zu casten ---
            for int_field in ['revisions', 'delivery_time_in_days']:
                if int_field in detail and not isinstance(detail[int_field], int):
                    try:
                        detail[int_field] = int(detail[int_field])
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(f"Detail {int_field} must be an integer.")
            # --- PATCH: Versuche, price in float zu casten ---
            if 'price' in detail and not isinstance(detail['price'], (int, float, type(None))):
                try:
                    detail['price'] = float(detail['price'])
                except (ValueError, TypeError):
                    raise serializers.ValidationError('Detail price must be a number.')
            if not isinstance(detail.get('title'), str):
                raise serializers.ValidationError('Detail title must be a string.')
            if not isinstance(detail.get('revisions'), int):
                raise serializers.ValidationError('Detail revisions must be an integer.')
            if not isinstance(detail.get('delivery_time_in_days'), int):
                raise serializers.ValidationError('Detail delivery_time_in_days must be an integer.')
            if not (isinstance(detail.get('price'), (int, float, type(None)))):
                raise serializers.ValidationError('Detail price must be a number.')
            if not isinstance(detail.get('features'), list):
                raise serializers.ValidationError('Detail features must be a list.')
            if not isinstance(detail.get('offer_type'), str):
                raise serializers.ValidationError('Detail offer_type must be a string.')
            for field in ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']:
                if field not in detail:
                    raise serializers.ValidationError(f"Each detail must include '{field}'.")
        # Accept empty string or None for optional fields
        if 'description' in data and (data['description'] is None or data['description'] == ''):
            data['description'] = ''
        return data

    def create(self, validated_data):
        image_base64 = validated_data.pop('image_base64', None)
        image = validated_data.pop('image', None)
        details = validated_data.pop('details', None)  # Details entfernen
        request = self.context.get('request')
        # Prüfe, ob owner explizit übergeben wurde (z.B. als ID)
        owner = validated_data.get('owner', None)
        if owner and not isinstance(owner, User):
            try:
                owner_obj = User.objects.get(pk=owner)
                validated_data['owner'] = owner_obj
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner': 'User does not exist.'})
        elif not owner:
            # Setze den aktuellen User als owner, falls nicht explizit übergeben
            if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
                validated_data['owner'] = request.user
            else:
                raise serializers.ValidationError({'owner': 'Owner must be provided or authenticated.'})
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
        # Details werden nicht gespeichert, aber für die API-Antwort genutzt
        offer._api_details = details
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

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'offer', 'created_at', 'status']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Set the user from the request context
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Only allow status to be updated
        if 'status' in validated_data:
            instance.status = validated_data['status']
            instance.save()
        return instance

# Dummy Review model/serializer for demonstration (replace with real model if available)
class ReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    business_user = serializers.IntegerField()
    reviewer = serializers.IntegerField()
    rating = serializers.IntegerField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
