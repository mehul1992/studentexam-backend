import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from typing import Dict, Any, Optional


class BaseAPIView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_json_data(self, request) -> Dict[str, Any]:
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError('Invalid JSON')
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> None:
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
    
    def success_response(self, data: Dict[str, Any], status: int = 200) -> JsonResponse:
        return JsonResponse(data, status=status)
    
    def error_response(self, message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({'detail': message}, status=status)
    
    def handle_exception(self, exception: Exception) -> JsonResponse:
        if isinstance(exception, ValueError):
            return self.error_response(str(exception), 400)
        elif isinstance(exception, (KeyError, AttributeError)):
            return self.error_response('Invalid data format', 400)
        else:
            return self.error_response('Internal server error', 500)


class AuthenticatedAPIView(BaseAPIView):
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request, 'student'):
            return self.error_response('Authentication required', 401)
        return super().dispatch(request, *args, **kwargs)