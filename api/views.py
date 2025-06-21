from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from rest_framework import parsers

from .serializers import (
    SuperUserSerializer, RegistrationSerializer, LoginSerializer, ProfileSerializer, OfferSerializer, OrderSerializer, ReviewSerializer
)
from .models import Profile, Offer, Order

# Create your views here.

class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, world!"})

class SuperUserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SuperUserSerializer

class ProfileDetailView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import ProfileSerializer
        return ProfileSerializer

class BusinessProfileListView(ListAPIView):
    serializer_class = None  # Wird dynamisch gesetzt
    permission_classes = [IsAuthenticated]  # Authentifizierung erforderlich
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['username', 'location', 'created_at']
    search_fields = ['username', 'location', 'first_name', 'last_name']
    pagination_class = None  # Pagination deaktiviert

    def get_queryset(self):
        return Profile.objects.filter(type='business')

    def get_serializer_class(self):
        from .serializers import ProfileSerializer
        return ProfileSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerProfileListView(ListAPIView):
    serializer_class = None  # Wird dynamisch gesetzt
    permission_classes = [IsAuthenticated]  # Authentifizierung erforderlich
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['username', 'location', 'created_at']
    search_fields = ['username', 'location', 'first_name', 'last_name']
    pagination_class = None  # Pagination deaktiviert

    def get_queryset(self):
        return Profile.objects.filter(type='customer')

    def get_serializer_class(self):
        from .serializers import ProfileSerializer
        return ProfileSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data.get('username')
            password = serializer.validated_data['password']
            # Prüfe, ob username wie eine E-Mail aussieht
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                username = username_or_email
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseInfoView(APIView):
    authentication_classes = []  # Deaktiviert jegliche Authentifizierung
    permission_classes = [AllowAny]
    def get(self, request):
        # Dummy-Daten, später dynamisch aus DB befüllen
        return Response({
            'offer_count': 0,
            'review_count': 0,
            'business_profile_count': 0,
            'average_rating': 0,
        }, status=status.HTTP_200_OK)

class ReviewsListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response([], status=status.HTTP_200_OK)

class OrdersListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response([], status=status.HTTP_200_OK)

class PublicProfileListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # Gebe ein leeres Array zurück, nicht ein Objekt
        return Response([], status=status.HTTP_200_OK)

class OfferListCreateView(ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def create(self, request, *args, **kwargs):
        print("Offer POST data:", dict(request.data))
        response = super().create(request, *args, **kwargs)
        print("Offer created response:", response.data)
        return response

class OfferDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

class OrderCountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        count = Order.objects.filter(user_id=user_id).count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)

class OfferDetailDummyView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        # pk: künstliche ID, z.B. 11, 12, 13
        offer_id = int(str(pk)[:-1]) if len(str(pk)) > 1 else 0
        type_map = {
            '1': ('basic', 'Basic Paket', 49.99, 3, 2, ['1x Beratung', 'E-Mail Support']),
            '2': ('standard', 'Standard Paket', 79.99, 2, 3, ['2x Beratung', 'Telefon Support']),
            '3': ('premium', 'Premium Paket', 129.99, 1, 5, ['Unbegrenzte Beratung', 'Premium Support']),
        }
        t = type_map.get(str(pk)[-1], type_map['1'])
        return Response({
            'id': pk,
            'title': t[1],
            'revisions': t[4],
            'delivery_time_in_days': t[3],
            'price': t[2],
            'features': t[5],
            'offer_type': t[0],
            'offer': offer_id,
        }, status=status.HTTP_200_OK)

class OrdersListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Pagination deaktiviert, gibt immer ein Array zurück

class OrderDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

# Dummy in-memory review list for demonstration
REVIEWS = []

class ReviewsListCreateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response(REVIEWS, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Prevent duplicate reviews by same reviewer for same business_user
            business_user = serializer.validated_data.get('business_user')
            reviewer = serializer.validated_data.get('reviewer')
            for review in REVIEWS:
                if review['business_user'] == business_user and review['reviewer'] == reviewer:
                    return Response({'detail': 'Duplicate review not allowed.'}, status=status.HTTP_400_BAD_REQUEST)
            review = serializer.data
            review['id'] = len(REVIEWS) + 1
            REVIEWS.append(review)
            return Response(review, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        review = next((r for r in REVIEWS if r['id'] == pk), None)
        if review:
            return Response(review, status=status.HTTP_200_OK)
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    def patch(self, request, pk):
        review = next((r for r in REVIEWS if r['id'] == pk), None)
        if not review:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            review.update(serializer.validated_data)
            return Response(review, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        global REVIEWS
        before = len(REVIEWS)
        REVIEWS = [r for r in REVIEWS if r['id'] != pk]
        if len(REVIEWS) < before:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
