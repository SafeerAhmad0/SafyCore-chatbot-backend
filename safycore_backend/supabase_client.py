"""
Supabase client configuration and utilities
"""
from supabase import create_client, Client
from django.conf import settings


def get_supabase_client() -> Client:
    """
    Get Supabase client instance with anon key (user-level access)
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase_admin_client() -> Client:
    """
    Get Supabase client with service role key (admin-level access)
    Use this for server-side operations that bypass RLS
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def get_user_supabase_client(access_token: str) -> Client:
    """
    Get Supabase client authenticated with user's JWT token
    This ensures Row Level Security (RLS) is enforced

    Args:
        access_token: User's JWT access token from Supabase auth

    Returns:
        Authenticated Supabase client
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    # Set the user's access token for all requests
    client.auth.set_session(access_token, access_token)

    return client
