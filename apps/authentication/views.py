from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import LoginSerializer, RegistrationSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """Authentifiziert einen Benutzer und liefert ein Authentifizierungs-Token zurück."""
        try:
            return self._login_user(request)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _login_user(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data.get('username')
            password = serializer.validated_data['password']
            username = self._get_username(username_or_email)
            if not username:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
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

    def _get_username(self, username_or_email):
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                return user_obj.username
            except User.DoesNotExist:
                return None
        return username_or_email

class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """Register a new user and return authentication token."""
        try:
            return self._register_user(request)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _register_user(self, request):
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


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Logout user by deleting their token."""
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'detail': 'Token not found.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'detail': 'Interner Serverfehler.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
