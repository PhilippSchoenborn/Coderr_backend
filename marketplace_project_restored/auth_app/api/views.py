from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    POST: Creates a new user account and returns an authentication token.
    Accepts username, email, password, and profile_type in the request body.
    Returns user details and authentication token on success.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user and return authentication token.
        
        Args:
            request: HTTP request containing username, email, password, and profile_type
            
        Returns:
            Response: User data with authentication token (201) or validation errors (400)
        """
        try:
            return self._register_user(request)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _register_user(self, request):
        """Handle user registration logic."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return self._success_response(user, token)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _success_response(self, user, token):
        """Create success response for authentication."""
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user authentication.
    
    POST: Authenticates a user with username/email and password.
    Returns an authentication token on successful login.
    Supports login with either username or email address.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate a user and return an authentication token.
        
        Args:
            request: HTTP request containing username/email and password
            
        Returns:
            Response: User data with authentication token (200) or error (400)
        """
        try:
            return self._login_user(request)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _login_user(self, request):
        """Handle user authentication logic."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        username_or_email = serializer.validated_data.get('username')
        password = serializer.validated_data['password']
        username = self._get_username(username_or_email)
        
        if not username:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
        return self._authenticate_user(username, password)

    def _authenticate_user(self, username, password):
        """Authenticate user and return token response."""
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    def _get_username(self, username_or_email):
        """
        Resolve username from email if needed.
        
        Args:
            username_or_email: Either a username or email address
            
        Returns:
            str: Username or None if email not found
        """
        if '@' in username_or_email:
            return self._get_username_from_email(username_or_email)
        return username_or_email

    def _get_username_from_email(self, email):
        """Get username from email address."""
        try:
            user_obj = User.objects.get(email=email)
            return user_obj.username
        except User.DoesNotExist:
            return None


class DashboardView(APIView):
    """
    Dashboard data endpoint.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get dashboard data for authenticated user."""
        user = request.user
        # TODO: Add actual dashboard data logic
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'message': 'Dashboard data'
        })


class BaseInfoView(APIView):
    """
    Platform statistics endpoint.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Get platform statistics."""
        from reviews_app.models import Review
        from profiles_app.models import Profile
        from offers_app.models import Offer
        
        stats = self._calculate_platform_stats()
        return Response(stats)

    def _calculate_platform_stats(self):
        """Calculate platform statistics."""
        from reviews_app.models import Review
        from profiles_app.models import Profile
        from offers_app.models import Offer
        
        review_stats = self._get_review_stats()
        business_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()
        
        return {
            **review_stats,
            'business_profile_count': business_count,
            'offer_count': offer_count
        }

    def _get_review_stats(self):
        """Get review statistics."""
        from reviews_app.models import Review
        from django.db.models import Avg
        
        reviews = Review.objects.all()
        review_count = reviews.count()
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        
        return {
            'review_count': review_count,
            'average_rating': round(average_rating, 1)
        }


class OrderCountView(APIView):
    """
    Get count of in_progress orders for a business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Get count of in_progress orders for business user."""
        from orders_app.models import Order
        
        try:
            business_user = User.objects.get(id=business_user_id)
            order_count = Order.objects.filter(
                offer_detail__offer__owner=business_user,
                status='in_progress'
            ).count()
            
            return Response({'order_count': order_count})
        except User.DoesNotExist:
            return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)


class CompletedOrderCountView(APIView):
    """
    Get count of completed orders for a business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Get count of completed orders for business user."""
        from orders_app.models import Order
        
        try:
            business_user = User.objects.get(id=business_user_id)
            completed_order_count = Order.objects.filter(
                offer_detail__offer__owner=business_user,
                status='completed'
            ).count()
            
            return Response({'completed_order_count': completed_order_count})
        except User.DoesNotExist:
            return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)


class HelloView(APIView):
    """
    Test endpoint.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Return hello message."""
        return Response({
            'message': 'Hello from Django Service Marketplace Backend!'
        })
