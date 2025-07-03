from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    User profile model extending Django's User model.
    """
    TYPE_CHOICES = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file = models.ImageField(upload_to='profiles/', blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    location = models.CharField(max_length=200, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles_profile'

    def __str__(self):
        return f"{self.user.username} - {self.type}"
