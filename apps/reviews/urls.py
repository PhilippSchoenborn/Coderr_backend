from django.urls import path
from .views import ReviewsListCreateView, ReviewDetailView

urlpatterns = [
    path('', ReviewsListCreateView.as_view(), name='reviews-list-create'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
