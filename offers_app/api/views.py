from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView,
    RetrieveAPIView, ListAPIView
)
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError
from django.http import Http404
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

    def list(self, request, *args, **kwargs):
        """Override list to handle validation errors."""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            if isinstance(e, ValidationError):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            raise

    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        # Validate query parameters first
        self._validate_query_params()
        
        queryset = (Offer.objects.all()
                    .select_related('owner')
                    .prefetch_related('offer_details'))

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

    def _validate_query_params(self):
        """Validate query parameters and raise ValidationError if invalid."""
        # Validate max_delivery_time parameter
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        print(f"DEBUG: max_delivery_time = {max_delivery_time}")
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                print(f"DEBUG: Converted to int: {max_delivery_time}")
                if max_delivery_time <= 0:
                    raise ValidationError(
                        {"max_delivery_time": "Delivery time must be a positive integer."}
                    )
            except (ValueError, TypeError) as e:
                print(f"DEBUG: ValueError/TypeError: {e}")
                raise ValidationError(
                    {"max_delivery_time": "Invalid delivery time. Must be a positive integer."}
                )

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

        # Max price filter - Filtert auf das min_price Feld des Angebots (<=)
        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                max_price = float(max_price)
                if max_price >= 0:
                    # Filter basierend auf der Annotation calculated_min_price (<= für
                    # maximum)
                    queryset = queryset.filter(calculated_min_price__lte=max_price)
            except (ValueError, TypeError):
                # Invalid values are ignored, return all offers
                pass

        # Exact price filter - Filtert nach exaktem min_price Wert (=)
        exact_price = self.request.query_params.get('exact_price')
        if exact_price:
            try:
                exact_price = float(exact_price)
                if exact_price >= 0:
                    # Filter basierend auf der Annotation calculated_min_price (= für exakt)
                    queryset = queryset.filter(calculated_min_price=exact_price)
            except (ValueError, TypeError):
                # Invalid values are ignored, return all offers
                pass

        # Max delivery time filter - Filtert auf das min_delivery_time Feld des
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
                # This should not happen as validation is done in get_queryset
                pass

        # Search filter (title and description)
        search = self.request.query_params.get('search')
        if search and search.strip():
            search = search.strip()
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            ).distinct()
            # If no results found after search, return empty queryset
            if not queryset.exists():
                return queryset.none()

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
    pagination_class = CustomPageNumberPagination  # Fix: Add pagination

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

    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        # Validate query parameters first
        self._validate_query_params()
        
        queryset = (Offer.objects.all()
                    .select_related('owner')
                    .prefetch_related('offer_details'))

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

    def _validate_query_params(self):
        """Validate query parameters and raise ValidationError if invalid."""
        # Validate max_delivery_time parameter
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        print(f"DEBUG: max_delivery_time = {max_delivery_time}")
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                print(f"DEBUG: Converted to int: {max_delivery_time}")
                if max_delivery_time <= 0:
                    raise ValidationError(
                        {"max_delivery_time": "Delivery time must be a positive integer."}
                    )
            except (ValueError, TypeError) as e:
                print(f"DEBUG: ValueError/TypeError: {e}")
                raise ValidationError(
                    {"max_delivery_time": "Invalid delivery time. Must be a positive integer."}
                )

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

        # Max price filter - Filtert auf das min_price Feld des Angebots (<=)
        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                max_price = float(max_price)
                if max_price >= 0:
                    # Filter basierend auf der Annotation calculated_min_price (<= für
                    # maximum)
                    queryset = queryset.filter(calculated_min_price__lte=max_price)
            except (ValueError, TypeError):
                # Invalid values are ignored, return all offers
                pass

        # Exact price filter - Filtert nach exaktem min_price Wert (=)
        exact_price = self.request.query_params.get('exact_price')
        if exact_price:
            try:
                exact_price = float(exact_price)
                if exact_price >= 0:
                    # Filter basierend auf der Annotation calculated_min_price (= für exakt)
                    queryset = queryset.filter(calculated_min_price=exact_price)
            except (ValueError, TypeError):
                # Invalid values are ignored, return all offers
                pass

        # Max delivery time filter - Filtert auf das min_delivery_time Feld des
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
                # This should not happen as validation is done in get_queryset
                pass

        # Search filter (title and description)
        search = self.request.query_params.get('search')
        if search and search.strip():
            search = search.strip()
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            ).distinct()
            # If no results found after search, return empty queryset
            if not queryset.exists():
                return queryset.none()

        # Creator ID filter
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            try:
                creator_id = int(creator_id)
                queryset = queryset.filter(owner_id=creator_id)
            except (ValueError, TypeError):
                pass

        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to handle validation errors."""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            if isinstance(e, ValidationError):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            raise

    def perform_create(self, serializer):
        """Perform object creation."""
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to return full offer data."""
        # Step 1: Check Authentication (401) first
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        
        # Step 2: Check Permissions (403) before validation
        self.check_permissions(request)
        
        # Step 3: Validate data (400) after authentication and permissions
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
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only owners can modify/delete offers, but we need to check business type first
            return [IsAuthenticated(), IsBusinessUser(), IsOwnerOnly()]
        else:
            # GET requests also require authentication according to documentation
            return [IsAuthenticated()]

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method in ['PUT', 'PATCH']:
            return OfferUpdateSerializer
        return OfferSerializer

    def update(self, request, *args, **kwargs):
        """Update the object."""
        # Step 1: Check Authentication (401) first
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        
        # Step 2: Check general permissions (403) before validation and object retrieval
        self.check_permissions(request)
        
        # Step 3: Validate data format (400) before object existence check
        partial = kwargs.pop('partial', False)
        # Pre-validate the data format without instance
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Step 4: Get object (404 if not found) - after validation
        instance = self.get_object()
        
        # Step 5: Final validation with instance
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        # Return full offer with details
        response_serializer = OfferSerializer(offer, context={'request': request})
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete the object."""
        # Step 1: Check Authentication (401) first
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        
        # Step 2: Check general permissions (403) before object retrieval
        self.check_permissions(request)
        
        # Step 3: Get object (404 if not found)
        instance = self.get_object()
        
        # Step 4: Delete object
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        """
        Override to ensure correct HTTP status code order: 401 -> 403 -> 404
        """
        # Step 1: Check Authentication (401) first for ALL methods (including GET)
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotAuthenticated()
        
        # Step 2: Check general permissions (403) before object retrieval for protected methods
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            for permission in self.get_permissions():
                if not permission.has_permission(self.request, self):
                    raise PermissionDenied()
        
        # Step 3: Get object (404 if not found)
        try:
            obj = super().get_object()
        except Http404:
            raise Http404()
        
        # Step 4: Check Object Permissions (403) for specific object on protected methods
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.check_object_permissions(self.request, obj)
        
        return obj


class OfferDetailDetailView(RetrieveAPIView):
    """
    Retrieve an individual offer detail.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Override to ensure correct HTTP status code order: 401 -> 404
        """
        # Check Authentication (401) first
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotAuthenticated()
        
        # Get object (404 if not found)
        return super().get_object()


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
