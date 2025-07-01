from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser


class OptionalTokenAuthentication(TokenAuthentication):
    """
    Token authentication that doesn't fail for invalid tokens.
    
    If a valid token is provided, the user is authenticated.
    If an invalid token is provided, the user remains anonymous.
    This allows public endpoints to work even when invalid tokens are sent.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        
        If authentication fails, return None instead of raising an exception.
        This allows the request to continue as an anonymous user.
        """
        try:
            return super().authenticate(request)
        except exceptions.AuthenticationFailed:
            # If token authentication fails, return None to allow anonymous access
            return None
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Token'
