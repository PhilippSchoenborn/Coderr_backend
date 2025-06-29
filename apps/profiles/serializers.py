from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model. Handles validation and serialization of user profile data,
    including custom validation for fields such as email, first name, last name, and others.
    Enforces required fields, forbidden fields, and type checks for PATCH/PUT requests.
    """
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, allow_blank=False, min_length=2, max_length=150)
    last_name = serializers.CharField(required=True, allow_blank=False, min_length=2, max_length=150)
    location = serializers.CharField(required=False, allow_blank=True, max_length=255)
    tel = serializers.CharField(required=False, allow_blank=True, max_length=50)
    description = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    working_hours = serializers.CharField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'type', 'created_at', 'username']

    def validate_email(self, value):
        """
        Ensure the email is unique among all users except the current instance.
        Raise a validation error if the email is already taken.
        """
        user_qs = User.objects.filter(email=value)
        if self.instance and self.instance.user:
            user_qs = user_qs.exclude(pk=self.instance.user.pk)
        if user_qs.exists():
            raise serializers.ValidationError('E-Mail-Adresse ist bereits vergeben.')
        return value

    def validate_first_name(self, value):
        """
        Ensure the first name is not empty and does not consist only of digits.
        """
        if not value.strip():
            raise serializers.ValidationError('Vorname darf nicht leer sein.')
        if value.isdigit():
            raise serializers.ValidationError('Vorname darf nicht nur aus Zahlen bestehen.')
        return value

    def validate_last_name(self, value):
        """
        Ensure the last name is not empty and does not consist only of digits.
        """
        if not value.strip():
            raise serializers.ValidationError('Nachname darf nicht leer sein.')
        if value.isdigit():
            raise serializers.ValidationError('Nachname darf nicht nur aus Zahlen bestehen.')
        return value

    def validate_description(self, value):
        """
        If provided, ensure the description is at least 5 characters long.
        """
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError('Beschreibung muss mindestens 5 Zeichen lang sein.')
        return value

    def validate_location(self, value):
        """
        If provided, ensure the location is at least 2 characters long.
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError('Ort muss mindestens 2 Zeichen lang sein.')
        return value

    def validate_working_hours(self, value):
        """
        If provided, ensure the working hours string is at least 2 characters long.
        """
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError('Arbeitszeiten müssen mindestens 2 Zeichen lang sein.')
        return value

    def validate(self, data):
        """
        Perform object-level validation:
        - Disallow extra fields not defined in the serializer.
        - Disallow changes to read-only fields.
        - Require at least one field to be provided.
        - Disallow None values for any field.
        """
        # Disallow extra fields
        allowed = set(self.fields.keys())
        extra = set(self.initial_data.keys()) - allowed
        if extra:
            raise serializers.ValidationError(f'Nicht erlaubte Felder: {", ".join(extra)}')
        # Disallow changes to read-only fields
        for field in self.Meta.read_only_fields:
            if field in self.initial_data:
                raise serializers.ValidationError(f'Feld "{field}" darf nicht geändert werden.')
        # No data provided
        if not self.initial_data:
            raise serializers.ValidationError('Es müssen Daten zum Aktualisieren angegeben werden.')
        # None values not allowed
        for k, v in self.initial_data.items():
            if v is None:
                raise serializers.ValidationError(f'Feld "{k}" darf nicht None sein.')
        return data
