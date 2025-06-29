from django.urls import path
from .views import OrdersListCreateView, CompletedOrderCountView, InProgressOrderCountView

urlpatterns = [
    path('', OrdersListCreateView.as_view(), name='orders-list-create'),
    path('completed-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('in-progress-count/<int:business_user_id>/', InProgressOrderCountView.as_view(), name='in-progress-order-count'),
]
