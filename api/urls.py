from django.urls import path
from .views import (
    HelloWorldView,
    SuperUserCreateView,
    ProfileDetailView,
    BusinessProfileListView,
    CustomerProfileListView,
    RegistrationView,
    LoginView,
    BaseInfoView,
    PublicProfileListView,
    ReviewsListView,
    OrdersListView,
    OfferListCreateView,
    OfferDetailView,
    OrderCountView,
    OfferDetailDummyView,  # Import ergänzt
)

urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello-world'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('profiles/', PublicProfileListView.as_view(), name='public-profiles'),
    path('reviews/', ReviewsListView.as_view(), name='reviews-list'),
    path('orders/', OrdersListView.as_view(), name='orders-list'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profiles'),
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailDummyView.as_view(), name='offerdetails-detail'),
    path('order-count/<int:user_id>/', OrderCountView.as_view(), name='order-count'),
    path('api/order-count/<int:user_id>/', OrderCountView.as_view(), name='order-count-api'),
]
