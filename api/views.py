from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, CreateAPIView
from rest_framework import filters

from .serializers import SuperUserSerializer
from .models import Profile

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
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['username', 'location', 'created_at']
    search_fields = ['username', 'location', 'first_name', 'last_name']

    def get_queryset(self):
        return Profile.objects.filter(type='business')

    def get_serializer_class(self):
        from .serializers import ProfileSerializer
        return ProfileSerializer

class CustomerProfileListView(ListAPIView):
    serializer_class = None  # Wird dynamisch gesetzt
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['username', 'location', 'created_at']
    search_fields = ['username', 'location', 'first_name', 'last_name']

    def get_queryset(self):
        return Profile.objects.filter(type='customer')

    def get_serializer_class(self):
        from .serializers import ProfileSerializer
        return ProfileSerializer
