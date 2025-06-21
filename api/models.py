from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    file = models.ImageField(upload_to='profiles/', blank=True, null=True)  # Profile picture
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Jetzt optional
    image = models.ImageField(upload_to='offers/', blank=True, null=True)  # Bildfeld für Angebote
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')

    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username} for {self.offer.title}"
