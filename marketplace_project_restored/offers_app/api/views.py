from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferCreateSerializer, OfferUpdateSerializer, OfferDetailSerializer
from .permissions import IsOwnerOrReadOnly, IsBusinessUser


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
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OfferDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an offer.
    """
    queryset = Offer.objects.all().select_related('owner').prefetch_related('offer_details')
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]
    
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
