"""
Supabase JWT authentication backend for Django REST Framework
"""
from rest_framework import authentication, exceptions
from django.conf import settings
from safycore_backend.supabase_client import get_supabase_client
from .models import UserProfile


class SupabaseAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that validates Supabase JWT tokens
    """

    def authenticate(self, request):
        """
        Authenticate the request using Supabase JWT token

        Returns:
            tuple: (user_profile, token) if authentication succeeds
            None: if no authentication is attempted
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # Verify token with Supabase
            supabase = get_supabase_client()
            user_response = supabase.auth.get_user(token)

            if not user_response or not user_response.user:
                raise exceptions.AuthenticationFailed('Invalid token')

            supabase_user = user_response.user

            # Get or create UserProfile
            user_profile, created = UserProfile.objects.get_or_create(
                user_id=supabase_user.id,
                defaults={'email': supabase_user.email}
            )

            # Store token in request for later use
            request.supabase_token = token
            request.supabase_user = supabase_user

            return (user_profile, token)

        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')

    def authenticate_header(self, request):
        """
        Return the WWW-Authenticate header value
        """
        return 'Bearer realm="api"'
