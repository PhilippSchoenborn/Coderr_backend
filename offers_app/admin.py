from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    model = OfferDetail
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['title', 'description', 'owner__username']
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['title', 'offer', 'price', 'delivery_time_in_days']
    list_filter = ['price', 'delivery_time_in_days']
    search_fields = ['title', 'offer__title']
