from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferListCreateView, OfferDetailView, OfferViewSet

router = DefaultRouter()
router.register(r'viewset', OfferViewSet)

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-list-create'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('', include(router.urls)),
]
