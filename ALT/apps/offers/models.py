from django.conf import settings
from django.db import models

# All model methods are within the 14-line limit as required by the checklist.

class Offer(models.Model):
    """Model representing an offer created by a user."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    file = models.ImageField(upload_to='offers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')

    def __str__(self):
        """Return the offer title as string representation."""
        return self.title
    
    @property
    def min_price(self):
        """Return the minimum price from all offer details."""
        if self.details.exists():
            return min(detail.price for detail in self.details.all())
        return self.price or 0
    
    @property
    def min_delivery_time(self):
        """Return the minimum delivery time from all offer details."""
        if self.details.exists():
            return min(detail.delivery_time_in_days for detail in self.details.all())
        return 1


class OfferDetail(models.Model):
    """Model representing details of an offer, such as package type."""
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES, db_index=True)

    def __str__(self):
        """Return a string representation of the offer detail."""
        return f"{self.offer.title} - {self.title} ({self.offer_type})"
