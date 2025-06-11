from django.test import TestCase
from django.contrib.auth import get_user_model


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
