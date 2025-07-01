from django.db import models
from django.contrib.auth.models import User
from offers_app.models import OfferDetail


class Order(models.Model):
    """
    Order model for tracking service orders.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} - {self.offer_detail.offer.title} ({self.status})"
    
    @property
    def business_user(self):
        """Get the business user who owns the offer."""
        return self.offer_detail.offer.owner
