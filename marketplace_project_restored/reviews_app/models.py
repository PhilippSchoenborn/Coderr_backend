from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Review model for customer reviews of business services.
    """
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews')
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews_review'
        ordering = ['-created_at']
        # One review per customer-business pair
        unique_together = ['reviewer', 'business_user']

    def __str__(self):
        return f"Review by {
            self.reviewer.username} for {
            self.business_user.username} ({
            self.rating}/5)"
