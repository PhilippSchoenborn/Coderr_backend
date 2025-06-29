from django.contrib.auth.models import User
from rest_framework import status, filters, parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from .models import Offer, OfferDetail
from apps.profiles.models import Profile
from .serializers import OfferSerializer
from core.permissions import IsOwnerOrReadOnly
from .business_logic import OfferBusinessLogic


class OfferListPagination(PageNumberPagination):
    page_size = 6  # Default page size as used in frontend
    page_size_query_param = 'page_size'
    max_page_size = 100


class OfferListCreateView(ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    pagination_class = OfferListPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['updated_at', 'created_at']
    search_fields = ['title', 'description']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Apply filters to the queryset based on query parameters."""
        from django.db.models import Min, Q
        
        queryset = Offer.objects.select_related('owner').prefetch_related('details').all()
        
        # Apply annotations for filtering
        queryset = queryset.annotate(
            min_detail_price=Min('details__price'),
            min_detail_delivery=Min('details__delivery_time_in_days')
        )
        
        # Apply filters
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
        
        # Apply custom ordering
        ordering = self.request.query_params.get('ordering')
        if ordering == 'updated_at':
            queryset = queryset.order_by('-updated_at')
        elif ordering == '-updated_at':
            queryset = queryset.order_by('-updated_at')
        else:
            queryset = queryset.order_by('-created_at')  # Default ordering
        
        return queryset

    def post(self, request, *args, **kwargs):
        """Create a new offer with business logic validation"""
        # Validate user permissions
        permission_error = OfferBusinessLogic.validate_user_permissions(request.user)
        if permission_error:
            return permission_error
        
        # Validate offer data
        data = request.data.copy()
        validation_error = OfferBusinessLogic.validate_offer_data(data)
        if validation_error:
            return validation_error
        
        # Create offer with details
        try:
            offer, details_objs = OfferBusinessLogic.create_offer_with_details(request.user, data)
            offer_data = OfferBusinessLogic.format_offer_response(offer, details_objs)
            return Response(offer_data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {'detail': 'Interner Serverfehler.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        return self._prepare_offer_creation(request, *args, **kwargs)

    def _prepare_offer_creation(self, request, *args, **kwargs):
        data = request.data.copy()
        for key in ['title', 'description', 'file']:
            if isinstance(data.get(key), list):
                data[key] = data[key][0]
        if not data.get('owner'):
            data['owner'] = request.user.pk
        owner_id = data.get('owner')
        if owner_id and not self._owner_exists(owner_id):
            return Response({'detail': 'Owner does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data)
        response = super().create(request, *args, **kwargs)
        return response

    def _owner_exists(self, owner_id):
        try:
            User.objects.get(pk=owner_id)
            return True
        except User.DoesNotExist:
            return False

class OfferDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def handle_exception(self, exc):
        return super().handle_exception(exc)

    def get_object(self):
        from rest_framework.exceptions import NotFound
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotFound()
        try:
            return super().get_object()
        except Exception:
            raise NotFound()

    def get(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            instance = self.get_object()
        except Exception:
            return Response({'detail': 'Angebot nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            details = instance.details.all()
            details_list = []
            for d in details:
                url = request.build_absolute_uri(f'/api/offerdetails/{d.id}/')
                details_list.append({'id': d.id, 'url': url})
            min_price = min([d.price for d in details]) if details else None
            min_delivery_time = min([d.delivery_time_in_days for d in details]) if details else None
            data = {
                'id': instance.id,
                'user': instance.owner.id if instance.owner else None,
                'title': instance.title,
                'image': instance.file.url if instance.file else None,
                'description': instance.description,
                'created_at': instance.created_at,
                'updated_at': instance.updated_at,
                'details': details_list,
                'min_price': min_price,
                'min_delivery_time': min_delivery_time,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        if self.request.user != self.get_object().owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to edit this offer.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to delete this offer.")
        instance.delete()

    def delete(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            instance = self.get_object()
        except Exception:
            return Response({'detail': 'Angebot nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user != instance.owner:
            return Response({'detail': 'Keine Berechtigung zum Löschen.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            self.perform_destroy(instance)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            instance = self.get_object()
        except Exception:
            return Response({'detail': 'Angebot nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user != instance.owner:
            return Response({'detail': 'Keine Berechtigung zum Bearbeiten.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        offer_fields = ['title', 'description', 'file']
        for field in offer_fields:
            if field in data:
                setattr(instance, field, data[field])
        try:
            instance.save()
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if 'details' in data:
            details_data = data['details']
            if not isinstance(details_data, list):
                return Response({'detail': 'details muss eine Liste sein.'}, status=status.HTTP_400_BAD_REQUEST)
            for detail_update in details_data:
                offer_type = detail_update.get('offer_type')
                if not offer_type:
                    return Response({'detail': 'offer_type muss für jedes Detail angegeben werden.'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    offer_detail = instance.details.get(offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    return Response({'detail': f'Kein Angebotsdetail mit offer_type {offer_type} gefunden.'}, status=status.HTTP_400_BAD_REQUEST)
                for key, value in detail_update.items():
                    if key != 'id' and hasattr(offer_detail, key):
                        setattr(offer_detail, key, value)
                try:
                    offer_detail.save()
                except Exception:
                    return Response({'detail': 'Fehler beim Speichern eines Angebotsdetails.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OfferViewSet(ModelViewSet):
    """ViewSet for managing Offer CRUD operations and list endpoint with query param validation."""
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        """Return permissions based on action (create requires authentication)."""
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        """List offers, return 400 if unknown query params are present."""
        allowed_params = {'page', 'page_size', 'ordering', 'search'}
        for param in request.query_params:
            if param not in allowed_params:
                return Response({'detail': f'Ungültiger Query-Parameter: {param}'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
