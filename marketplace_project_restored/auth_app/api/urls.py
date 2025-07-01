from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('base-info/', views.BaseInfoView.as_view(), name='base-info'),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('order-count/<int:business_user_id>/', views.OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', views.CompletedOrderCountView.as_view(), name='completed-order-count'),
]
