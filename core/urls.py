from django.urls import path
from .views import BaseInfoView
from apps.offers.urls import offer_detail_urls
from apps.orders.urls import order_count_urls

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
] + offer_detail_urls + order_count_urls
