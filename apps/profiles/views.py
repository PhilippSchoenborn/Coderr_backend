from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Profile
from .serializers import ProfileSerializer

class ProfileDetailView(RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's profile."""
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the ProfileSerializer class."""
        return ProfileSerializer

    def patch(self, request, *args, **kwargs):
        """Update the user's own profile. Only the owner can patch their profile."""
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = self.get_object()
        except Exception:
            return Response({'detail': 'Profil nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        if profile.user != request.user:
            return Response({'detail': 'Sie dürfen nur Ihr eigenes Profil bearbeiten.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        serializer = ProfileSerializer(profile, data=data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # E-Mail separat im User-Objekt speichern
        if 'email' in serializer.validated_data:
            profile.user.email = serializer.validated_data['email']
            profile.user.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """Retrieve the authenticated user's profile."""
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = self.get_object()
        except Exception:
            return Response({'detail': 'Profil nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            response_data = {
                'user': profile.user.id if profile.user else None,
                'username': profile.username,
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'file': profile.file.name if profile.file else None,
                'location': profile.location or '',
                'tel': profile.tel or '',
                'description': profile.description or '',
                'working_hours': profile.working_hours or '',
                'type': profile.type,
                'email': profile.user.email if profile.user else '',
                'created_at': profile.created_at,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileListView(ReadOnlyModelViewSet):
    """List profiles by type (customer or business). Auth required."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['username', 'location', 'created_at']
    search_fields = ['username', 'location', 'first_name', 'last_name']
    pagination_class = None

    def get_queryset(self):
        """Return queryset filtered by type if provided."""
        profile_type = self.request.query_params.get('type')
        if profile_type in ['customer', 'business']:
            return Profile.objects.filter(type=profile_type)
        return Profile.objects.all()

    def list(self, request, *args, **kwargs):
        """List all profiles for the authenticated user, optionally filtered by type."""
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentifizierung erforderlich.'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.filter_queryset(self.get_queryset())
        profiles = [
            {
                'user': profile.user.id if profile.user else None,
                'username': profile.username,
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'location': profile.location or '',
                'tel': profile.tel or '',
                'description': profile.description or '',
                'working_hours': profile.working_hours or '',
                'file': profile.file.name if profile.file else None,
                'type': profile.type
            }
            for profile in queryset
        ]
        return Response(profiles, status=status.HTTP_200_OK)
