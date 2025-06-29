from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferListCreateView, OfferDetailView, OfferViewSet
from core.views import OfferDetailDetailView

router = DefaultRouter()
router.register(r'viewset', OfferViewSet)

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-list-create'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('', include(router.urls)),
]

# Add offerdetails endpoint to main backend urls
offer_detail_urls = [
    path('offerdetails/<int:pk>/', OfferDetailDetailView.as_view(), name='offerdetails-detail'),
]
