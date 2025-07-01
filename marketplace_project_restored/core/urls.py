"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from auth_app.api.views import RegisterView, LoginView, BaseInfoView, OrderCountView, CompletedOrderCountView, DashboardView

def api_root(request):
    """Root API endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Django Service Marketplace API',
        'version': '1.0',
        'endpoints': {
            'registration': '/api/registration/',
            'login': '/api/login/',
            'dashboard': '/api/dashboard/',
            'profile': '/api/profile/{pk}/',
            'profiles_business': '/api/profiles/business/',
            'profiles_customer': '/api/profiles/customer/',
            'offers': '/api/offers/',
            'offerdetails': '/api/offerdetails/{id}/',
            'orders': '/api/orders/',
            'order_count': '/api/order-count/{business_user_id}/',
            'completed_order_count': '/api/completed-order-count/{business_user_id}/',
            'reviews': '/api/reviews/',
            'base_info': '/api/base-info/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('api/', api_root, name='api-root'),  # Root API endpoint
    path('admin/', admin.site.urls),
    
    # Exact specification endpoints
    path('api/registration/', RegisterView.as_view(), name='api-registration'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/dashboard/', DashboardView.as_view(), name='api-dashboard'),
    path('api/base-info/', BaseInfoView.as_view(), name='api-base-info'),
    path('api/order-count/<int:business_user_id>/', OrderCountView.as_view(), name='api-order-count'),
    path('api/completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='api-completed-order-count'),
    
    # App-specific endpoints
    path('api/profile/', include('profiles_app.api.urls')),   # For /api/profile/{pk}/
    path('api/profiles/', include('profiles_app.api.urls')),  # For /api/profiles/business/, customer/
    path('api/offers/', include('offers_app.api.urls')),      # For /api/offers/ endpoints
    path('api/offerdetails/', include('offers_app.api.detail_urls')), # For /api/offerdetails/{id}/
    path('api/orders/', include('orders_app.api.urls')),      # For /api/orders/ endpoints
    path('api/reviews/', include('reviews_app.api.urls')),    # For /api/reviews/ endpoints
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
