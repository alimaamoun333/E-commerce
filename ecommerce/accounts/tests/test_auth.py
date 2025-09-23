# accounts/tests/test_auth.py
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthTests(APITestCase):
    def test_register_and_auto_login(self):
        url = reverse("register")
        data = {
            "username": "tester",
            "email": "t@test.com",
            "password": "strongpassword123",
            "password2": "strongpassword123",
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("username", resp.data)
        # After register we logged in, session cookie should exist
        r = self.client.get(reverse("profile"))
        self.assertEqual(r.status_code, 200)
        self.assertIn("bio", r.data)

    def test_login_logout(self):
        User.objects.create_user(username="bob", password="pass12345")
        login_url = reverse("login")
        resp = self.client.post(login_url, {"username": "bob", "password": "pass12345"}, format="json")
        self.assertEqual(resp.status_code, 200)
        # Access protected
        r = self.client.get(reverse("profile"))
        self.assertEqual(r.status_code, 200)
        # Logout
        logout_url = reverse("logout")
        r2 = self.client.post(logout_url, format="json")
        self.assertEqual(r2.status_code, 200)
        # Now protected should be 403/401 (depends)
        r3 = self.client.get(reverse("profile"))
        self.assertIn(r3.status_code, (401, 403))
