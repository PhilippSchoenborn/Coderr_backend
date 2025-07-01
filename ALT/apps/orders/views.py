from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import PermissionDenied
from .models import Order
from .serializers import OrderSerializer
from .business_logic import OrderBusinessLogic

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        count, error = OrderBusinessLogic.get_order_count_for_business(
            business_user_id, 'completed'
        )
        if error:
            return Response({'detail': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)

class InProgressOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        count, error = OrderBusinessLogic.get_order_count_for_business(
            business_user_id, 'in_progress'
        )
        if error:
            return Response({'detail': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'order_count': count}, status=status.HTTP_200_OK)

class OrderCountView(APIView):
    """Combined view for order count (in-progress orders)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        count, error = OrderBusinessLogic.get_order_count_for_business(
            business_user_id, 'in_progress'
        )
        if error:
            return Response({'detail': error}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'order_count': count}, status=status.HTTP_200_OK)

class OrdersListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None

    def get_permissions(self):
        """Set permissions based on the HTTP method."""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticated()]  # All methods require authentication
    
    def post(self, request, *args, **kwargs):
        # Validate customer profile
        profile, error = OrderBusinessLogic.validate_customer_profile(request.user)
        if error:
            status_code = status.HTTP_403_FORBIDDEN if "Nur Kunden" in error else status.HTTP_404_NOT_FOUND
            return Response({'detail': error}, status=status_code)
        
        # Validate offer detail
        offer_detail, error = OrderBusinessLogic.validate_offer_detail_id(
            request.data.get('offer_detail_id')
        )
        if error:
            status_code = status.HTTP_400_BAD_REQUEST if "muss" in error else status.HTTP_404_NOT_FOUND
            return Response({'detail': error}, status=status_code)
        
        # Create order
        order, error = OrderBusinessLogic.create_order(request.user, offer_detail)
        if error:
            status_code = status.HTTP_404_NOT_FOUND if "nicht gefunden" in error else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response({'detail': error}, status=status_code)
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_staff:
            return Response({'detail': 'You do not have permission to delete this order.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = self.get_object()
        except Exception:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            self.perform_destroy(instance)
        except Exception:
            return Response({'detail': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """Detail view for individual order operations (PATCH/DELETE)"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        order = super().get_object()
        # Check permissions using business logic
        if not OrderBusinessLogic.check_order_access_permission(self.request.user, order):
            raise PermissionDenied("You do not have permission to access this order.")
        return order
