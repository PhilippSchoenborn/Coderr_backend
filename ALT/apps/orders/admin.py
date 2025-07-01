from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    list_display = ('id', 'user', 'offer', 'offer_detail', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'offer__title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'offer', 'offer_detail', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
