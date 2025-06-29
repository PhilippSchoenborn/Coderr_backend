from django.urls import path
from .views import OrdersListCreateView, CompletedOrderCountView, InProgressOrderCountView, OrderDetailView, OrderCountView

urlpatterns = [
    path('', OrdersListCreateView.as_view(), name='orders-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('completed-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('in-progress-count/<int:business_user_id>/', InProgressOrderCountView.as_view(), name='in-progress-order-count'),
]
