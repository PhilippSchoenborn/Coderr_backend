from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from apps.offers.models import Offer, OfferDetail
from apps.profiles.models import Profile
from apps.orders.models import Order
from apps.offers.serializers import OfferSerializer
from apps.orders.serializers import OrderSerializer
from apps.profiles.serializers import ProfileSerializer
from apps.reviews.views import REVIEWS

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def handle_exception(self, exc):
        return super().handle_exception(exc)

    def get(self, request):
        try:
            user = request.user
            offers = Offer.objects.filter(owner=user)
            orders = Order.objects.filter(offer__owner=user)
            offers_data = OfferSerializer(offers, many=True, context={'request': request}).data
            orders_data = OrderSerializer(orders, many=True, context={'request': request}).data
            return Response({
                'offers': offers_data,
                'orders': orders_data,
                'profile': ProfileSerializer(user.profile, context={'request': request}).data if hasattr(user, 'profile') else None
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class BaseInfoView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            # Zugriff auf REVIEWS in try/except, damit Patch im Test korrekt Fehler auslöst
            review_count = len(REVIEWS)
            if review_count > 0:
                average_rating = round(sum(r.get('rating', 0) for r in REVIEWS) / review_count, 2)
            else:
                average_rating = 0.0
            offer_count = Offer.objects.count()
            business_profile_count = Profile.objects.filter(type='business').count()
            return Response({
                'review_count': review_count,
                'average_rating': average_rating,
                'business_profile_count': business_profile_count,
                'offer_count': offer_count,
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, world!"})

class PublicProfileListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response([], status=status.HTTP_200_OK)

class MyOffersListView(ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Offer.objects.filter(owner=self.request.user)

class PublicOfferListView(ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['updated_at', 'min_detail_price']
    search_fields = ['title', 'description']

    def get_queryset(self):
        from django.db.models import Min, Q
        
        queryset = Offer.objects.select_related('owner').prefetch_related('details').all()
        
        # Apply annotations for filtering
        queryset = queryset.annotate(
            min_detail_price=Min('details__price'),
            min_detail_delivery=Min('details__delivery_time_in_days')
        )
        
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        search = self.request.query_params.get('search')
        
        if creator_id:
            queryset = queryset.filter(owner_id=creator_id)
        
        if min_price:
            try:
                min_price_val = float(min_price)
                queryset = queryset.filter(min_detail_price__gte=min_price_val)
            except (ValueError, TypeError):
                pass
        
        if max_delivery_time:
            try:
                max_delivery_val = int(max_delivery_time)
                queryset = queryset.filter(min_detail_delivery__lte=max_delivery_val)
            except (ValueError, TypeError):
                pass
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # Remove duplicates and apply ordering
        queryset = queryset.distinct()
        
        ordering = self.request.query_params.get('ordering')
        if ordering == 'updated_at':
            queryset = queryset.order_by('-updated_at')
        elif ordering == 'min_price' or ordering == 'min_detail_price':
            queryset = queryset.order_by('min_detail_price')
        else:
            queryset = queryset.order_by('-created_at')  # Default ordering
            
        return queryset

class OfferDetailDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            offer_detail = OfferDetail.objects.get(pk=pk)
        except OfferDetail.DoesNotExist:
            return Response({'detail': 'Angebotsdetail nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = {
            'id': offer_detail.id,
            'title': offer_detail.title,
            'revisions': offer_detail.revisions,
            'delivery_time_in_days': offer_detail.delivery_time_in_days,
            'price': offer_detail.price,
            'features': offer_detail.features,
            'offer_type': offer_detail.offer_type,
        }
        return Response(data, status=status.HTTP_200_OK)
