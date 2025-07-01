from django.urls import path
from . import views

urlpatterns = [
    # For /api/offerdetails/ endpoints - individual offer details
    path('<int:pk>/', views.OfferDetailDetailView.as_view(), name='offer-detail-detail'),
]
