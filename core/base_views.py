"""
Base API views following SOLID, DRY, and KISS principles.
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from typing import Dict, Any, Optional


class BaseAPIView(View):
    """
    Base API view that provides common functionality for all API endpoints.
    Follows DRY principle by eliminating code duplication.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_json_data(self, request) -> Dict[str, Any]:
        """
        Safely parse JSON data from request body.
        Returns parsed data or raises ValueError with appropriate message.
        """
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError('Invalid JSON')
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> None:
        """
        Validate that all required fields are present in the data.
        Raises ValueError if any field is missing.
        """
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
    
    def success_response(self, data: Dict[str, Any], status: int = 200) -> JsonResponse:
        """Create a standardized success response."""
        return JsonResponse(data, status=status)
    
    def error_response(self, message: str, status: int = 400) -> JsonResponse:
        """Create a standardized error response."""
        return JsonResponse({'detail': message}, status=status)
    
    def handle_exception(self, exception: Exception) -> JsonResponse:
        """
        Handle common exceptions and return appropriate error responses.
        """
        if isinstance(exception, ValueError):
            return self.error_response(str(exception), 400)
        elif isinstance(exception, (KeyError, AttributeError)):
            return self.error_response('Invalid data format', 400)
        else:
            return self.error_response('Internal server error', 500)


class AuthenticatedAPIView(BaseAPIView):
    """
    Base view for endpoints that require authentication.
    Follows Single Responsibility Principle by handling auth concerns.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if student is authenticated
        if not hasattr(request, 'student'):
            return self.error_response('Authentication required', 401)
        return super().dispatch(request, *args, **kwargs)
