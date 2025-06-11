from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


class UserManagerTests(TestCase):
    def test_create_user_without_password(self):
        User = get_user_model()
        user = User.objects.create_user(email="user@example.com")
        self.assertFalse(user.has_usable_password())

    def test_create_superuser_with_password(self):
        User = get_user_model()
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("adminpass"))

    def test_create_superuser_without_password_raises(self):
        User = get_user_model()
        with self.assertRaises(TypeError):
            User.objects.create_superuser(email="nopass@example.com")


class AuthEndpointTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("user-register")
        self.login_url = reverse("user-login")

    def test_register_user(self):
        data = {"email": "new@example.com", "password": "strongpass"}
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_register_invalid_data(self):
        data = {"email": "bad@example.com"}  # missing password
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_login_valid_credentials(self):
        User = get_user_model()
        User.objects.create_user(email="user2@example.com", password="pass1234")
        data = {"email": "user2@example.com", "password": "pass1234"}
        resp = self.client.post(self.login_url, data, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_login_invalid_credentials(self):
        User = get_user_model()
        User.objects.create_user(email="user3@example.com", password="pass1234")
        data = {"email": "user3@example.com", "password": "wrong"}
        resp = self.client.post(self.login_url, data, format="json")
        self.assertEqual(resp.status_code, 400)
