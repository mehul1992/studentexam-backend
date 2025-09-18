import os
import json
import jwt
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.conf import settings
from students.models import Student


def _jwt_secret() -> str:
    return getattr(settings, 'JWT_AUTH', {}).get('JWT_SECRET_KEY', os.environ.get('JWT_SECRET', 'dev-secret-change-me'))


class JwtAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Only guard API routes
        path = request.path or ''
        if not path.startswith('/api/'):
            return None

        # Allow unauthenticated login endpoint
        if path == '/api/auth/login':
            return None

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)

        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(token, _jwt_secret(), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'detail': 'Token has expired.'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'detail': 'Invalid token.'}, status=401)

        if payload.get('type') != 'access':
            return JsonResponse({'detail': 'Invalid token type.'}, status=401)

        customer_id = payload.get('sub')
        if not customer_id:
            return JsonResponse({'detail': 'Invalid token payload.'}, status=401)

        try:
            student = Student.objects.get(id=customer_id, is_active=True)
        except Student.DoesNotExist:
            return JsonResponse({'detail': 'User not found or inactive.'}, status=401)

        # Attach to request for views
        request.student = student
        return None


