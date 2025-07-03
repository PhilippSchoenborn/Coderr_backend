from django.urls import path
from . import views

urlpatterns = [
    # For /api/profile/ endpoints
    path(
        '<int:pk>/',
        views.ProfileDetailView.as_view(),
        name='profile-detail'),
    # GET/PATCH /api/profile/{pk}/

    # For /api/profiles/ endpoints
    path('', views.ProfileView.as_view(), name='profile-root'),  # Root endpoint
    path(
        '<int:user_id>/',
        views.ProfileByUserIdView.as_view(),
        name='profile-by-user-id'),
    path(
        'profile/<int:pk>/',
        views.ProfileDetailView.as_view(),
        name='profile-detail-legacy'),
    path('profile/', views.ProfileView.as_view(), name='profile-legacy'),
    path('business/', views.BusinessProfileListView.as_view(),
         name='business-profiles'),
    path('customer/', views.CustomerProfileListView.as_view(),
         name='customer-profiles'),
]
