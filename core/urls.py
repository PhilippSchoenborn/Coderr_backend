from django.urls import path
from .views import (
    BaseInfoView, OfferDetailDetailView, DashboardView, 
    HelloWorldView, PublicProfileListView, MyOffersListView, 
    PublicOfferListView
)
from apps.orders.views import OrderCountView
from apps.authentication.views import LoginView, RegistrationView, LogoutView

urlpatterns = [
    # Authentication endpoints (originally under /api/)
    path('login/', LoginView.as_view(), name='login'),
    path('login', LoginView.as_view(), name='login-no-slash'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('registration', RegistrationView.as_view(), name='registration-no-slash'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout', LogoutView.as_view(), name='logout-no-slash'),
    
    # Core endpoints
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('base-info', BaseInfoView.as_view(), name='base-info-no-slash'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('hello/', HelloWorldView.as_view(), name='hello-world'),
    path('public-profiles/', PublicProfileListView.as_view(), name='public-profiles'),
    path('my-offers/', MyOffersListView.as_view(), name='my-offers'),
    path('public-offers/', PublicOfferListView.as_view(), name='public-offers'),
    path('offerdetails/<int:pk>/', OfferDetailDetailView.as_view(), name='offerdetails-detail'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
]
