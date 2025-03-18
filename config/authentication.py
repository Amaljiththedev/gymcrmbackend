# config/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
import logging

logger = logging.getLogger(__name__)

class JWTAuthentication(BaseJWTAuthentication):
    """
    Custom authentication that looks for the JWT in the 'access_token' cookie.
    Falls back to header-based authentication if not found.
    """
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        
        # For security, avoid logging the raw token in production.
        if raw_token:
            logger.debug("JWT token found in cookies.")
        else:
            logger.debug("No JWT token in cookies; falling back to header-based authentication.")
            return super().authenticate(request)
        
        try:
            validated_token = self.get_validated_token(raw_token)
        except TokenError as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            return None
        
        user = self.get_user(validated_token)
        return (user, validated_token)
