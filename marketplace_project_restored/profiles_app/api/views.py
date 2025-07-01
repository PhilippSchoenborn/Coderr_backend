from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django.contrib.auth.models import User
from ..models import Profile
from .serializers import ProfileSerializer, ProfileUpdateSerializer


class ProfileView(APIView):
    """
    API endpoint to retrieve and update the authenticated user's profile.
    
    GET: Returns the current user's profile information
    PATCH: Updates the current user's profile (partial updates allowed)
    
    Users can only access and modify their own profile.
    Profile ownership is determined by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the authenticated user's profile.
        
        Returns:
            Response: Profile data or error message
        """
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """
        Update the authenticated user's profile (partial update).
        
        Args:
            request: HTTP request with profile data to update
            
        Returns:
            Response: Updated profile data or validation errors
        """
        try:
            profile = request.user.profile
            return self._update_profile(profile, request.data)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def _update_profile(self, profile, data):
        """Update profile with provided data."""
        serializer = ProfileUpdateSerializer(profile, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = ProfileSerializer(profile)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(ListAPIView):
    """
    API endpoint to list all business profiles.
    
    Returns a list of all profiles with type='business'.
    """
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    queryset = Profile.objects.filter(type='business').select_related('user')
    pagination_class = None  # Disable pagination


class CustomerProfileListView(ListAPIView):
    """
    API endpoint to list all customer profiles.
    
    Returns a list of all profiles with type='customer'.
    """
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    queryset = Profile.objects.filter(type='customer').select_related('user')
    pagination_class = None  # Disable pagination


class ProfileDetailView(RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update a specific profile by ID.
    
    GET: Returns profile information for the specified user ID (public access)
    PATCH: Updates the profile (only if user owns the profile)
    
    Users can only modify their own profile.
    """
    queryset = Profile.objects.all().select_related('user')
    serializer_class = ProfileSerializer
    
    def get_permissions(self):
        """Allow public read access, require authentication for updates."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_object(self):
        """Get profile by user ID from URL parameter."""
        user_id = self.kwargs.get('pk')
        try:
            user = User.objects.get(id=user_id)
            return user.profile
        except (User.DoesNotExist, Profile.DoesNotExist):
            return None
    
    def get(self, request, *args, **kwargs):
        """Retrieve profile by user ID."""
        profile = self.get_object()
        if profile is None:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        """Update profile (only own profile)."""
        profile = self.get_object()
        if profile is None:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if not self._user_owns_profile(profile, request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        return self._update_profile_data(profile, request.data)

    def _user_owns_profile(self, profile, user):
        """Check if user owns the profile."""
        return profile.user == user

    def _update_profile_data(self, profile, data):
        """Update profile with validation."""
        serializer = ProfileUpdateSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ProfileSerializer(profile)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileByUserIdView(RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update a specific profile by user ID.
    
    GET: Returns profile information for the specified user ID
    PATCH: Updates the profile (only if user owns the profile)
    
    Users can only modify their own profile.
    """
    queryset = Profile.objects.all().select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get profile by user ID from URL parameter."""
        user_id = self.kwargs.get('user_id')  # Changed from 'pk' to 'user_id'
        try:
            user = User.objects.get(id=user_id)
            return user.profile
        except (User.DoesNotExist, Profile.DoesNotExist):
            return None
    
    def get(self, request, *args, **kwargs):
        """Retrieve profile by user ID."""
        profile = self.get_object()
        if profile is None:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        """Update profile (only own profile)."""
        profile = self.get_object()
        if profile is None:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        return self._handle_profile_update(profile, request)

    def _handle_profile_update(self, profile, request):
        """Handle profile update with ownership check."""
        if profile.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        return self._perform_profile_update(profile, request.data)

    def _perform_profile_update(self, profile, data):
        """Perform the actual profile update."""
        serializer = ProfileUpdateSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ProfileSerializer(profile)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
