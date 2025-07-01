from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from django.db.models import Q
from ..models import Order
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
)
from .permissions import (
    IsAdminOrOrderRelatedUser, IsAdminOrBusinessOwner
)


class OrderListCreateView(ListCreateAPIView):
    """
    List orders or create a new order.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """Return filtered queryset."""
        user = self.request.user
        # Return orders where user is either customer or business owner
        return Order.objects.filter(
            Q(customer=user) | Q(offer_detail__offer__owner=user)
        ).select_related('customer', 'offer_detail__offer__owner').prefetch_related('offer_detail')

    def perform_create(self, serializer):
        """Perform order creation."""
        # Only customer users can create orders
        if not hasattr(
                self.request.user,
                'profile') or self.request.user.profile.type != 'customer':
            raise PermissionDenied("Only customer users can create orders.")
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Override create to return full order data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return the created order with full data using OrderSerializer
        order = serializer.instance
        response_serializer = OrderSerializer(order)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an order.
    """
    queryset = Order.objects.all().select_related('customer',
                                                  'offer_detail__offer__owner').prefetch_related('offer_detail')
    serializer_class = OrderSerializer

    def get_permissions(self):
        """Return appropriate permissions."""
        if self.request.method in ['PUT', 'PATCH']:
            # Only business owners and admins can update orders
            return [IsAuthenticated(), IsAdminOrBusinessOwner()]
        elif self.request.method == 'DELETE':
            # Only admins can delete orders
            return [IsAuthenticated(), IsAdminOrOrderRelatedUser()]
        else:
            # Anyone related to the order can view it
            return [IsAuthenticated(), IsAdminOrOrderRelatedUser()]

    def get_object(self):
        """Get object and handle permissions properly."""
        try:
            obj = super().get_object()
            self.check_object_permissions(self.request, obj)
            return obj
        except Order.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Order not found.")
        except PermissionDenied:
            # Re-raise as 403, not 401
            raise PermissionDenied("You do not have permission to access this order.")


class OrderStatusUpdateView(APIView):
    """
    Update order status.
    """
    permission_classes = [IsAuthenticated, IsAdminOrBusinessOwner]

    def patch(self, request, pk):
        """Update order status."""
        try:
            order = Order.objects.get(pk=pk)
            self.check_object_permissions(request, order)

            return self._update_order_status(order, request.data)
        except Order.DoesNotExist:
            return Response({
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def _update_order_status(self, order, data):
        """Update order status and return response."""
        serializer = OrderStatusUpdateSerializer(order, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
