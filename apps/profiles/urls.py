from django.urls import path
from .views import ProfileDetailView, ProfileListView

urlpatterns = [
    path('<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('', ProfileListView.as_view({'get': 'list'}), name='profile-list'),
]
