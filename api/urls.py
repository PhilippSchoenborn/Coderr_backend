from django.urls import path
from .views import (
    HelloWorldView,
    SuperUserCreateView,
    ProfileDetailView,
    BusinessProfileListView,
    CustomerProfileListView,
)

urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello-world'),
    path('registration/', SuperUserCreateView.as_view(), name='superuser-registration'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profiles'),
]
