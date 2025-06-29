from rest_framework import serializers

class ReviewSerializer(serializers.Serializer):
    """
    Serializer for review data. Used for validating and serializing review submissions.
    """
    business_user = serializers.IntegerField(help_text="ID of the business user being reviewed.")
    rating = serializers.IntegerField(help_text="Rating value (e.g., 1-5 stars).")
    description = serializers.CharField(help_text="Textual description of the review.")
