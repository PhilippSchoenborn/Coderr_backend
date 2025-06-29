from django.urls import path
from .views import ProfileDetailView, ProfileListView

urlpatterns = [
    path('<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('business/', ProfileListView.as_view({'get': 'list'}), {'type': 'business'}, name='business-profiles'),
    path('customer/', ProfileListView.as_view({'get': 'list'}), {'type': 'customer'}, name='customer-profiles'),
    path('', ProfileListView.as_view({'get': 'list'}), name='profile-list'),
]
