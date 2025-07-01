from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from ..models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer
from .permissions import IsAuthorOrReadOnly, IsCustomerUser


class ReviewListCreateView(ListCreateAPIView):
    """
    List all reviews or create a new review.
    """
    queryset = Review.objects.all().select_related('reviewer', 'business_user')
    pagination_class = None  # Disable pagination
    
    def get_queryset(self):
        """Return filtered queryset."""
        queryset = Review.objects.all().select_related('reviewer', 'business_user')
        
        # Filter by business_user_id
        business_user_id = self.request.query_params.get('business_user_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        
        # Filter by reviewer_id
        reviewer_id = self.request.query_params.get('reviewer_id')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        """Return appropriate permissions."""
        if self.request.method == 'POST':
            return [IsCustomerUser()]
        return [AllowAny()]  # Reviews are publicly readable
    
    def perform_create(self, serializer):
        """Perform review creation."""
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        """Override create to return full review data."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the created review with full data using ReviewSerializer
        review = serializer.instance
        response_serializer = ReviewSerializer(review)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a review.
    """
    queryset = Review.objects.all().select_related('reviewer', 'business_user')
    permission_classes = [IsAuthorOrReadOnly]
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewUpdateSerializer
        return ReviewSerializer
    
    def update(self, request, *args, **kwargs):
        """Override update to return full review data."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        # Return full review with all fields
        response_serializer = ReviewSerializer(review)
        return Response(response_serializer.data)
