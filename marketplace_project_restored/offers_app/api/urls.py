from django.urls import path
from . import views

urlpatterns = [
    # For /api/offers/ endpoints
    path('', views.OfferListCreateView.as_view(), name='offer-list-create'),
    path('<int:pk>/', views.OfferDetailView.as_view(), name='offer-detail'),
]
