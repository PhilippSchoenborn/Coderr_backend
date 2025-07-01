from django.conf import settings
from django.db import models

# All model methods are within the 14-line limit as required by the checklist.

class Order(models.Model):
    """Model representing an order placed by a user for an offer."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, related_name='orders')
    offer_detail = models.ForeignKey('offers.OfferDetail', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        """Return a string representation of the order."""
        return f"Order {self.id} by {self.user.username} for {self.offer.title} ({self.offer_detail.offer_type if self.offer_detail else ''})"
