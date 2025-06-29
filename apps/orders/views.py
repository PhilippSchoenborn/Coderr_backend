from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from .models import Order
from apps.profiles.models import Profile
from apps.offers.models import Offer, OfferDetail
from .serializers import OrderSerializer

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, business_user_id):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            business_profile = Profile.objects.get(user_id=business_user_id, type='business')
        except Profile.DoesNotExist:
            return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        completed_order_count = Order.objects.filter(offer__owner=business_user_id, status='completed').count()
        return Response({'completed_order_count': completed_order_count}, status=status.HTTP_200_OK)

class InProgressOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, business_user_id):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            business_profile = Profile.objects.get(user_id=business_user_id, type='business')
        except Profile.DoesNotExist:
            return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        order_count = Order.objects.filter(offer__owner=business_user_id, status='in_progress').count()
        return Response({'order_count': order_count}, status=status.HTTP_200_OK)

class OrdersListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def post(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Kein Profil gefunden.'}, status=status.HTTP_401_UNAUTHORIZED)
        if profile.type != 'customer':
            return Response({'detail': 'Nur Kunden dürfen Bestellungen anlegen.'}, status=status.HTTP_403_FORBIDDEN)
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({'detail': 'offer_detail_id muss angegeben werden.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            offer_detail_id_int = int(offer_detail_id)
        except (ValueError, TypeError):
            return Response({'detail': 'offer_detail_id muss eine Zahl sein.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            offer_detail = OfferDetail.objects.get(pk=offer_detail_id_int)
        except OfferDetail.DoesNotExist:
            return Response({'detail': 'Angebotsdetail nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        offer = offer_detail.offer
        if not offer:
            return Response({'detail': 'Kein zugehöriges Angebot gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            order = Order.objects.create(
                user=request.user,
                offer=offer,
                offer_detail=offer_detail,
                status='in_progress',
            )
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
