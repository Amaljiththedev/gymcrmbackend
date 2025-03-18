import logging
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)
User = get_user_model()

# -------------------------------------------------------------------
# Manager Login (expects email & password)
# -------------------------------------------------------------------
class ManagerLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=email, password=password)
        if user is None or user.user_type != 'manager':
            logger.warning(f"Invalid manager login attempt for email: {email}")
            return Response({'error': 'Invalid credentials or not a manager account.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            response = Response({"message": "Manager login successful"}, status=status.HTTP_200_OK)
            
            # Set tokens in HTTP-only cookies
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            
                max_age=86400  # 1 day in seconds
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=86400
            )
            logger.info(f"Manager '{email}' logged in successfully.")
            return response
        except Exception as e:
            logger.error(f"Error during manager login for email '{email}': {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------------------------------------------------------
# Staff Login (expects username & password)
# -------------------------------------------------------------------
class StaffLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Assuming you have a custom authentication backend for staff login (or handle it here)
        user = authenticate(request, username=username, password=password)
        if user is None or user.user_type != 'staff':
            logger.warning(f"Invalid staff login attempt for username: {username}")
            return Response({'error': 'Invalid credentials or not a staff account.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            response = Response({"message": "Staff login successful"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
               
                max_age=86400
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
             
                max_age=86400
            )
            logger.info(f"Staff '{username}' logged in successfully.")
            return response
        except Exception as e:
            logger.error(f"Error during staff login for username '{username}': {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------------------------------------------------------
# Logout View (blacklists the refresh token and deletes cookies)
# -------------------------------------------------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError as e:
                logger.error(f"Error blacklisting token: {str(e)}")
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token', domain="localhost")
        response.delete_cookie('refresh_token', domain="localhost")
        return response

# -------------------------------------------------------------------
# User Profile View (returns minimal profile information)
# -------------------------------------------------------------------
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        profile_data = {
            "email": user.email,
            "role": user.user_type,  # Returns either 'manager' or 'staff'
        }
        return Response(profile_data, status=status.HTTP_200_OK)

# -------------------------------------------------------------------
# CSRF Token View (for clients to obtain a CSRF token)
# -------------------------------------------------------------------
class CSRFTokenView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'csrfToken': get_token(request)}, status=status.HTTP_200_OK)

# -------------------------------------------------------------------
# Admin Only View (restricted access to managers)
# -------------------------------------------------------------------
class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        if request.user.user_type == 'manager':
            return Response({"message": "Welcome, Manager!"}, status=status.HTTP_200_OK)
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

# -------------------------------------------------------------------
# Refresh Token View (blacklists old token and issues new tokens)
# -------------------------------------------------------------------
class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "No refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Optionally blacklist the old token
            new_refresh = RefreshToken.for_user(token.user)
            new_access = str(new_refresh.access_token)
            response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=new_access,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                domain="localhost",
                max_age=86400
            )
            response.set_cookie(
                key='refresh_token',
                value=str(new_refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                domain="localhost",
                max_age=86400
            )
            return response
        except TokenError as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
