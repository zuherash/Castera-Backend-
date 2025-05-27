import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class ClerkAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            request.user = AnonymousUser()
            return

        token = auth_header.split(' ')[1]
        try:
            resp = requests.get(
                'https://api.clerk.dev/v1/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            if resp.status_code != 200:
                raise AuthenticationFailed("Invalid Clerk token")

            data = resp.json()
            email = data.get('email_addresses', [{}])[0].get('email_address', '')
            full_name = data.get('first_name', '') + " " + data.get('last_name', '')
            image = data.get('image_url', '')
            role = 'admin' if data.get('private_metadata', {}).get('role') == 'admin' else 'user'

            user, created = User.objects.get_or_create(email=email)
            if created or user.full_name != full_name:
                user.full_name = full_name
                user.image = image
                user.role = role
                user.save()

            request.user = user

        except Exception as e:
            request.user = AnonymousUser()
