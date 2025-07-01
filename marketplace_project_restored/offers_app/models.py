from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """
    Service offer model.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    file = models.ImageField(upload_to='offers/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offers_offer'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def min_price(self):
        """Return the minimum price from offer details."""
        if self.offer_details.exists():
            return self.offer_details.aggregate(min_price=models.Min('price'))['min_price']
        return None
    
    @property
    def min_delivery_time(self):
        """Return the minimum delivery time from offer details."""
        if self.offer_details.exists():
            return self.offer_details.aggregate(min_time=models.Min('delivery_time_in_days'))['min_time']
        return None


class OfferDetail(models.Model):
    """
    Offer detail/pricing tier model.
    """
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='offer_details')
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES, db_index=True, default='basic')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offers_offerdetail'
    
    def __str__(self):
        return f"{self.offer.title} - {self.title} ({self.offer_type})"
