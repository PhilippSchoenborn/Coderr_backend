from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status

class ServerBasicTests(APITestCase):
    def test_hello_world(self):
        url = reverse('hello-world')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    def test_registration_superuser(self):
        url = reverse('superuser-registration')
        data = {
            'username': 'adminuser',
            'password': 'TestPassword123',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='adminuser').exists())

    def test_profile_list_unauthenticated(self):
        url = reverse('business-profiles')
        response = self.client.get(url)
        self.assertIn(response.status_code, [401, 403])

# Create your tests here.
