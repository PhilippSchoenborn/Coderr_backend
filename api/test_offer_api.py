import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Offer
from rest_framework.authtoken.models import Token

class OfferApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apitest', password='apitest123')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_create_offer_with_image_and_details(self):
        with open('media/offers/cat-6723256_1920.jpg', 'rb') as img:
            details = [
                {"title": "Basic", "revisions": 2, "delivery_time_in_days": 3, "price": 49.99, "features": ["Beratung"], "offer_type": "basic"},
                {"title": "Standard", "revisions": 3, "delivery_time_in_days": 2, "price": 79.99, "features": ["Support"], "offer_type": "standard"},
                {"title": "Premium", "revisions": 5, "delivery_time_in_days": 1, "price": 129.99, "features": ["Premium Support"], "offer_type": "premium"}
            ]
            response = self.client.post(
                '/api/offers/',
                {
                    'title': 'Testangebot',
                    'description': 'Testbeschreibung',
                    'details': json.dumps(details),
                    'image': img
                },
                format='multipart'
            )
        print('API RESPONSE:', response.status_code, response.json())
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('image', data)
        self.assertIn('details', data)
        self.assertTrue(data['image'])
        self.assertTrue(isinstance(data['details'], list))
        self.assertTrue('price' in data and data['price'] is not None)
        self.assertTrue('delivery_time_in_days' in data and data['delivery_time_in_days'] is not None)
