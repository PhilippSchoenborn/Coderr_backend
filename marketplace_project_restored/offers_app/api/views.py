from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView,
    RetrieveAPIView, ListAPIView
)
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Min
from ..models import Offer, OfferDetail
from .serializers import (
    OfferSerializer, OfferCreateSerializer,
    OfferUpdateSerializer, OfferDetailSerializer
)
from .permissions import IsBusinessUser, IsOwnerOnly


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination for public offers."""
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    page_size = 10
    max_page_size = 100

    def get_page_size(self, request):
        """Get page size from request."""
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size:
            try:
                page_size = int(page_size)
                if page_size > 0:
                    return min(page_size, self.max_page_size)
            except ValueError:
                pass
        return self.page_size


class PublicOfferListView(ListAPIView):
    """
    Public list of offers with filtering, search, and pagination.
    """
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        queryset = Offer.objects.all().select_related('owner').prefetch_related('offer_details')

        # Always annotate with min_price and min_delivery_time for consistent filtering
        queryset = queryset.annotate(
            calculated_min_price=Min('offer_details__price'),
            calculated_min_delivery=Min('offer_details__delivery_time_in_days')
        )

        # Apply filters
        queryset = self._apply_filters(queryset)

        # Apply ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        valid_orderings = [
            'created_at',
            '-created_at',
            'updated_at',
            '-updated_at',
            'min_price',
            '-min_price']

        if ordering in valid_orderings:
            if ordering == 'min_price':
                queryset = queryset.order_by('calculated_min_price')
            elif ordering == '-min_price':
                queryset = queryset.order_by('-calculated_min_price')
            else:
                queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def _apply_filters(self, queryset):
        """Apply filters based on query parameters."""
        # KORREKT: Filter direkt auf die berechneten min_price und
        # min_delivery_time Felder

        # Min price filter - Filtert auf das min_price Feld des Angebots (>=)
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                min_price = float(min_price)
                if min_price >= 0:
                    # Filter basierend auf der Annotation calculated_min_price (>= für
                    # minimum)
                    queryset = queryset.filter(calculated_min_price__gte=min_price)
            except (ValueError, TypeError):
                # Invalid values are ignored, return all offers
                pass

        # Min delivery time filter - Filtert auf das min_delivery_time Feld des
        # Angebots (<=)
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                if max_delivery_time > 0:
                    # Filter basierend auf der Annotation calculated_min_delivery (<=
                    # für maximum)
                    queryset = queryset.filter(
                        calculated_min_delivery__lte=max_delivery_time)
            except (ValueError, TypeError):
                # Invalid values are ignored, return all offers
                pass

        # Search filter (title and description)
        search = self.request.query_params.get('search')
        if search and search.strip():
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            ).distinct()

        # Creator ID filter
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            try:
                creator_id = int(creator_id)
                queryset = queryset.filter(owner_id=creator_id)
            except (ValueError, TypeError):
                pass

        return queryset


class OfferListCreateView(ListCreateAPIView):
    """
    List all offers or create a new offer.
    """
    queryset = Offer.objects.all().select_related('owner').prefetch_related('offer_details')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferSerializer

    def get_permissions(self):
        """Return appropriate permissions."""
        if self.request.method == 'POST':
            return [IsBusinessUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Perform object creation."""
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to return full offer data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return the created offer with full data using OfferSerializer
        offer = serializer.instance
        response_serializer = OfferSerializer(offer, context={'request': request})
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)


class OfferDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an offer.
    """
    queryset = Offer.objects.all().select_related('owner').prefetch_related('offer_details')

    def get_permissions(self):
        """Return appropriate permissions."""
        # All methods (including GET) require ownership
        return [IsAuthenticated(), IsOwnerOnly()]

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method in ['PUT', 'PATCH']:
            return OfferUpdateSerializer
        return OfferSerializer

    def update(self, request, *args, **kwargs):
        """Update the object."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        # Return full offer with details
        response_serializer = OfferSerializer(offer, context={'request': request})
        return Response(response_serializer.data)


class OfferDetailDetailView(RetrieveAPIView):
    """
    Retrieve an individual offer detail.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]


class MyOffersView(ListAPIView):
    """
    Get authenticated user's offers.
    """
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Get current user's offers."""
        return Offer.objects.filter(owner=self.request.user).select_related(
            'owner').prefetch_related('offer_details')
