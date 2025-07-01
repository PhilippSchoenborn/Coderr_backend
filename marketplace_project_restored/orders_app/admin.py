from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'offer_title', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'offer_detail__offer__title']

    def offer_title(self, obj):
        """Return offer title for admin display."""
        return obj.offer_detail.offer.title
    offer_title.short_description = 'Offer Title'
