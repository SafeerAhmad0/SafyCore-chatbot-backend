"""
User authentication views using Supabase
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from safycore_backend.supabase_client import get_supabase_client
from .models import UserProfile


class SignupView(APIView):
    """
    User signup endpoint - creates user in Supabase
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            supabase = get_supabase_client()

            # Sign up user in Supabase
            auth_response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })

            if not auth_response.user:
                return Response(
                    {'error': 'Failed to create user'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create UserProfile in Django
            user_profile = UserProfile.objects.create(
                user_id=auth_response.user.id,
                email=auth_response.user.email
            )

            return Response({
                'message': 'User created successfully',
                'user': {
                    'id': user_profile.user_id,
                    'email': user_profile.email
                },
                'access_token': auth_response.session.access_token if auth_response.session else None,
                'refresh_token': auth_response.session.refresh_token if auth_response.session else None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    """
    User login endpoint - authenticates with Supabase
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            supabase = get_supabase_client()

            # Sign in user with Supabase
            auth_response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })

            if not auth_response.user or not auth_response.session:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get or create UserProfile
            user_profile, created = UserProfile.objects.get_or_create(
                user_id=auth_response.user.id,
                defaults={'email': auth_response.user.email}
            )

            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user_profile.user_id,
                    'email': user_profile.email
                },
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    User logout endpoint
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            supabase = get_supabase_client()
            token = request.supabase_token

            # Sign out from Supabase
            supabase.auth.sign_out()

            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileView(APIView):
    """
    Get user profile information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user

        return Response({
            'user': {
                'id': user_profile.user_id,
                'email': user_profile.email,
                'created_at': user_profile.created_at,
                'default_session_id': user_profile.default_session_id
            }
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update user profile
        """
        user_profile = request.user

        # Update default_session_id if provided
        if 'default_session_id' in request.data:
            user_profile.default_session_id = request.data['default_session_id']
            user_profile.save()

        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': user_profile.user_id,
                'email': user_profile.email,
                'default_session_id': user_profile.default_session_id
            }
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Request password reset - sends email with reset link
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            supabase = get_supabase_client()

            # Send password reset email
            # Supabase will send email with reset link automatically
            supabase.auth.reset_password_email(email)

            return Response({
                'message': 'Password reset email sent. Please check your inbox.',
                'email': email
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Don't reveal if email exists or not (security best practice)
            return Response({
                'message': 'If an account with that email exists, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with new password
    """
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')  # From reset link
        new_password = request.data.get('new_password')

        if not access_token or not new_password:
            return Response(
                {'error': 'Access token and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            supabase = get_supabase_client()

            # Set session with the reset token
            supabase.auth.set_session(access_token, access_token)

            # Update password
            supabase.auth.update_user({
                'password': new_password
            })

            return Response({
                'message': 'Password updated successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to reset password: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    """
    Change password for authenticated user (while logged in)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'error': 'Current password and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_profile = request.user
            supabase = get_supabase_client()

            # Verify current password by attempting to sign in
            try:
                supabase.auth.sign_in_with_password({
                    'email': user_profile.email,
                    'password': current_password
                })
            except Exception:
                return Response(
                    {'error': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update to new password
            token = request.supabase_token
            supabase.auth.set_session(token, token)
            supabase.auth.update_user({
                'password': new_password
            })

            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to change password: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
