from django.contrib import admin
from .models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin configuration for Offer model."""
    list_display = ('title', 'owner', 'price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'owner', 'price')
        }),
        ('Content', {
            'fields': ('description', 'file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin configuration for OfferDetail model."""
    list_display = ('title', 'offer', 'offer_type', 'price', 'delivery_time_in_days')
    list_filter = ('offer_type',)
    search_fields = ('title', 'offer__title')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'offer', 'offer_type')
        }),
        ('Details', {
            'fields': ('features', 'price', 'delivery_time_in_days', 'revisions')
        }),
    )
