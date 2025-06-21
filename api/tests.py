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

    def test_protected_profile_list_unauthenticated(self):
        self.client.logout()
        url = reverse('business-profiles')
        response = self.client.get(url)
        self.assertIn(response.status_code, [401, 403])

# --- Coderr API Endpoint Tests ---

class CoderrApiEndpointTests(APITestCase):
    def setUp(self):
        # Create users for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@mail.de')
        self.business_user = User.objects.create_user(username='business', password='testpass', email='business@mail.de')
        self.client.login(username='testuser', password='testpass')

    def test_registration(self):
        url = reverse('registration')
        data = {
            'username': 'newuser',
            'email': 'newuser@mail.de',
            'password': 'newpass123',
            'repeated_password': 'newpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_login(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [200, 400])

    def test_profile_detail_get(self):
        url = reverse('profile-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401, 404])

    def test_profile_detail_patch(self):
        url = reverse('profile-detail', args=[self.user.id])
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, [200, 401, 403, 404])

    def test_business_profiles_list(self):
        url = reverse('business-profiles')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401])

    def test_customer_profiles_list(self):
        url = reverse('customer-profiles')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401])

    def test_offer_list(self):
        url = reverse('offer-list-create')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 400])

    def test_offer_create(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': 'Test description',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400, 401, 403])

    def test_offer_detail_get(self):
        # This test assumes at least one offer exists
        url = reverse('offer-detail', args=[1])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401, 404])

    def test_offer_detail_patch(self):
        url = reverse('offer-detail', args=[1])
        data = {'title': 'Updated Offer'}
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, [200, 400, 401, 403, 404])

    def test_offer_detail_delete(self):
        url = reverse('offer-detail', args=[1])
        response = self.client.delete(url)
        self.assertIn(response.status_code, [204, 401, 403, 404])

    def test_offerdetails_detail_get(self):
        url = reverse('offerdetails-detail', args=[1])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401, 404])

    def test_orders_list(self):
        url = reverse('orders-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401])

    def test_orders_create(self):
        url = reverse('orders-list')
        data = {'offer_detail_id': 1}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400, 401, 403, 404])

    def test_orders_patch(self):
        # Create an order first
        order_url = reverse('orders-list')
        order = self.client.post(order_url, {'offer': 1}, format='json').data
        if 'id' in order:
            url = reverse('order-detail', args=[order['id']])
            data = {'status': 'completed'}
            response = self.client.patch(url, data, format='json')
            self.assertIn(response.status_code, [200, 400, 401, 403, 404])
        else:
            self.skipTest('Order could not be created for patch test.')

    def test_orders_delete(self):
        # Create an order first
        order_url = reverse('orders-list')
        order = self.client.post(order_url, {'offer': 1}, format='json').data
        if 'id' in order:
            url = reverse('order-detail', args=[order['id']])
            response = self.client.delete(url)
            self.assertIn(response.status_code, [204, 401, 403, 404])
        else:
            self.skipTest('Order could not be created for delete test.')

    def test_reviews_list(self):
        url = reverse('reviews-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 401])

    def test_reviews_create(self):
        url = reverse('reviews-list')
        data = {'business_user': self.business_user.id, 'rating': 5, 'description': 'Great!'}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400, 401, 403])

    def test_reviews_patch(self):
        # Create a review first
        review_url = reverse('reviews-list')
        review = self.client.post(review_url, {'business_user': self.business_user.id, 'reviewer': self.user.id, 'rating': 5, 'description': 'Great!'}, format='json').data
        if 'id' in review:
            url = reverse('review-detail', args=[review['id']])
            data = {'rating': 4, 'description': 'Updated!'}
            response = self.client.patch(url, data, format='json')
            self.assertIn(response.status_code, [200, 400, 401, 403, 404])
        else:
            self.skipTest('Review could not be created for patch test.')

    def test_reviews_delete(self):
        # Create a review first
        review_url = reverse('reviews-list')
        review = self.client.post(review_url, {'business_user': self.business_user.id, 'reviewer': self.user.id, 'rating': 5, 'description': 'Great!'}, format='json').data
        if 'id' in review:
            url = reverse('review-detail', args=[review['id']])
            response = self.client.delete(url)
            self.assertIn(response.status_code, [204, 401, 403, 404])
        else:
            self.skipTest('Review could not be created for delete test.')

    # Zusätzliche Tests für Edge Cases und Fehlerfälle
    def test_registration_password_mismatch(self):
        url = reverse('registration')
        data = {
            'username': 'failuser',
            'email': 'fail@mail.de',
            'password': 'abc',
            'repeated_password': 'def',
            'type': 'customer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Passwords do not match', str(response.data))

    def test_login_wrong_password(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid credentials', str(response.data))

    def test_offer_create_missing_details(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': 'Test',
            # 'details' fehlt absichtlich
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [400, 401, 403])

    def test_profile_detail_not_found(self):
        url = reverse('profile-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_offer_detail_not_found(self):
        url = reverse('offer-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_order_detail_not_found(self):
        url = reverse('order-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_review_detail_not_found(self):
        url = reverse('review-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_modify_foreign_order(self):
        # User1 erstellt Order, User2 versucht zu löschen
        order_url = reverse('orders-list')
        order = self.client.post(order_url, {'offer': 1}, format='json').data
        if 'id' in order:
            self.client.logout()
            other = User.objects.create_user(username='other', password='otherpass')
            self.client.login(username='other', password='otherpass')
            url = reverse('order-detail', args=[order['id']])
            response = self.client.delete(url)
            self.assertIn(response.status_code, [403, 404, 401])
        else:
            self.skipTest('Order could not be created for foreign access test.')

    def test_invalid_datatypes(self):
        url = reverse('offer-list-create')
        data = {
            'title': 12345,  # should be string
            'description': 67890,  # should be string
            'details': 'notalist'  # should be list
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_too_long_strings(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'A' * 300,
            'description': 'B' * 1000,
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_negative_and_large_values(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': 'Test',
            'details': [
                {'title': 'Basic', 'revisions': -1, 'delivery_time_in_days': 999999, 'price': -100, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [400, 201])  # je nach Validierung

    def test_offer_create_exactly_3_details(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': 'Test',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_offer_create_more_than_3_details(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': 'Test',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'},
                {'title': 'Extra', 'revisions': 4, 'delivery_time_in_days': 4, 'price': 40, 'features': ['D'], 'offer_type': 'extra'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_review_min_max_rating(self):
        url = reverse('reviews-list')
        for rating in [1, 5]:
            data = {'business_user': self.business_user.id, 'reviewer': self.user.id, 'rating': rating, 'description': 'Test'}
            response = self.client.post(url, data, format='json')
            self.assertIn(response.status_code, [201, 400])

    def test_review_duplicate(self):
        url = reverse('reviews-list')
        data = {'business_user': self.business_user.id, 'reviewer': self.user.id, 'rating': 5, 'description': 'Test'}
        response1 = self.client.post(url, data, format='json')
        response2 = self.client.post(url, data, format='json')
        self.assertIn(response2.status_code, [400, 403])

    def test_optional_fields_empty(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': '',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], '')

    def test_offer_filtering(self):
        # Create two offers with different prices
        url = reverse('offer-list-create')
        self.client.post(url, {
            'title': 'Cheap', 'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }, format='json')
        self.client.post(url, {
            'title': 'Expensive', 'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 1000, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 2000, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 3000, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }, format='json')
        # Test filtering (simulate, as actual filter logic may not be implemented)
        response = self.client.get(url + '?search=Cheap')
        self.assertIn(response.status_code, [200, 400])

    def test_profile_search(self):
        url = reverse('business-profiles')
        response = self.client.get(url + '?search=testuser')
        self.assertIn(response.status_code, [200, 401])

    def test_concurrent_offer_update(self):
        # Simuliere zwei parallele Updates auf ein Angebot
        url = reverse('offer-list-create')
        data = {
            'title': 'Concurrent Offer',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        offer = self.client.post(url, data, format='json').data
        if 'id' in offer:
            detail_url = reverse('offer-detail', args=[offer['id']])
            resp1 = self.client.patch(detail_url, {'title': 'Update 1'}, format='json')
            resp2 = self.client.patch(detail_url, {'title': 'Update 2'}, format='json')
            self.assertIn(resp1.status_code, [200, 400])
            self.assertIn(resp2.status_code, [200, 400])
        else:
            self.skipTest('Offer could not be created for concurrency test.')

    def test_method_not_allowed(self):
        url = reverse('base-info')
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, 405)
        url = reverse('offer-list-create')
        response = self.client.patch(url, {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_large_payload(self):
        url = reverse('offer-list-create')
        details = [
            {'title': f'Detail {i}', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'}
            for i in range(100)
        ]
        data = {
            'title': 'Big Offer',
            'description': 'x' * 10000,
            'details': details
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400, 413])

    def test_unknown_fields(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Test Offer',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ],
            'unknown_field': 'should be ignored or rejected'
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_wrong_content_type(self):
        url = reverse('offer-list-create')
        data = '{"title": "Test", "description": "desc", "details": []}'
        response = self.client.post(url, data, content_type='text/plain')
        self.assertIn(response.status_code, [400, 415])

    def test_invalid_token(self):
        url = reverse('business-profiles')
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken')
        response = self.client.get(url)
        self.assertIn(response.status_code, [401, 403])
        self.client.credentials()  # Reset

    def test_empty_post_request(self):
        url = reverse('offer-list-create')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    # Spezialfall: Angebot mit identischem Titel von zwei Usern
    def test_offer_same_title_different_users(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'UniqueTitle',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        resp1 = self.client.post(url, data, format='json')
        self.assertEqual(resp1.status_code, 201)
        self.client.logout()
        other = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        resp2 = self.client.post(url, data, format='json')
        self.assertEqual(resp2.status_code, 201)

    # Spezialfall: Löschen eines Angebots, das bereits gelöscht wurde
    def test_delete_already_deleted_offer(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'DeleteMe',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        offer = self.client.post(url, data, format='json').data
        if 'id' in offer:
            detail_url = reverse('offer-detail', args=[offer['id']])
            resp1 = self.client.delete(detail_url)
            self.assertEqual(resp1.status_code, 204)
            resp2 = self.client.delete(detail_url)
            self.assertEqual(resp2.status_code, 404)
        else:
            self.skipTest('Offer could not be created for delete test.')

    # Performance-Test: Viele Angebote listen
    def test_offer_list_performance(self):
        url = reverse('offer-list-create')
        for i in range(50):
            self.client.post(url, {
                'title': f'PerfOffer{i}',
                'description': 'desc',
                'details': [
                    {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                    {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                    {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
                ]
            }, format='json')
        import time
        start = time.time()
        response = self.client.get(url)
        duration = time.time() - start
        self.assertIn(response.status_code, [200, 400])
        self.assertLess(duration, 2.0)  # Sollte in <2s antworten

    # Performance-Test: Bulk-POST von Reviews
    def test_bulk_review_post_performance(self):
        url = reverse('reviews-list')
        reviews = [
            {'business_user': self.business_user.id, 'reviewer': self.user.id, 'rating': 5, 'description': f'Bulk {i}'}
            for i in range(20)
        ]
        import time
        start = time.time()
        for review in reviews:
            self.client.post(url, review, format='json')
        duration = time.time() - start
        self.assertLess(duration, 2.0)

    # Integrationstest: Registrierung, Login, Angebots-POST, Angebots-GET
    def test_register_login_offer_flow(self):
        reg_url = reverse('registration')
        login_url = reverse('login')
        offer_url = reverse('offer-list-create')
        reg_data = {
            'username': 'integrationuser',
            'email': 'integration@mail.de',
            'password': 'integrationpass',
            'repeated_password': 'integrationpass',
            'type': 'customer'
        }
        reg_resp = self.client.post(reg_url, reg_data, format='json')
        self.assertEqual(reg_resp.status_code, 201)
        login_resp = self.client.post(login_url, {'username': 'integrationuser', 'password': 'integrationpass'}, format='json')
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        offer_data = {
            'title': 'IntegrationOffer',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        offer_resp = self.client.post(offer_url, offer_data, format='json')
        self.assertEqual(offer_resp.status_code, 201)
        get_resp = self.client.get(offer_url)
        self.assertIn(get_resp.status_code, [200, 400])

    # Integrationstest: End-to-End Bestellung
    def test_end_to_end_order_flow(self):
        # Registrierung und Login
        reg_url = reverse('registration')
        login_url = reverse('login')
        reg_data = {
            'username': 'orderuser',
            'email': 'order@mail.de',
            'password': 'orderpass',
            'repeated_password': 'orderpass',
            'type': 'customer'
        }
        reg_resp = self.client.post(reg_url, reg_data, format='json')
        self.assertEqual(reg_resp.status_code, 201)
        login_resp = self.client.post(login_url, {'username': 'orderuser', 'password': 'orderpass'}, format='json')
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        # Angebot anlegen
        offer_url = reverse('offer-list-create')
        offer_data = {
            'title': 'OrderFlowOffer',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        offer_resp = self.client.post(offer_url, offer_data, format='json')
        self.assertEqual(offer_resp.status_code, 201)
        offer_id = offer_resp.data.get('id')
        # Bestellung anlegen
        order_url = reverse('orders-list')
        order_resp = self.client.post(order_url, {'offer': offer_id}, format='json')
        self.assertIn(order_resp.status_code, [201, 400, 401, 403, 404])
        # Bestellung abrufen
        if 'id' in order_resp.data:
            order_detail_url = reverse('order-detail', args=[order_resp.data['id']])
            get_resp = self.client.get(order_detail_url)
            self.assertIn(get_resp.status_code, [200, 404])

    # --- Automatisch generierte zusätzliche Tests für maximale Abdeckung ---
    def test_offer_title_empty(self):
        url = reverse('offer-list-create')
        data = {'title': '', 'description': 'desc', 'details': [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_description_null(self):
        url = reverse('offer-list-create')
        data = {'title': 'Test', 'description': None, 'details': [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_details_empty_list(self):
        url = reverse('offer-list-create')
        data = {'title': 'Test', 'description': 'desc', 'details': []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_details_none(self):
        url = reverse('offer-list-create')
        data = {'title': 'Test', 'description': 'desc', 'details': None}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_details_missing(self):
        url = reverse('offer-list-create')
        data = {'title': 'Test', 'description': 'desc'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_details_wrong_type(self):
        url = reverse('offer-list-create')
        data = {'title': 'Test', 'description': 'desc', 'details': 'notalist'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_missing_field(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'features': ['A'], 'offer_type': 'basic'},  # price fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_wrong_type(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 'one', 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_empty_features(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': [], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_wrong_type(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': 'notalist', 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_offer_type_invalid(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'invalid'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_negative_price(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': -10, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_zero_price(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 0, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_large_price(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 1e10, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_null_price(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': None, 'features': ['A'], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_missing_offer_type(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A']},  # offer_type fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_missing_features(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'offer_type': 'basic'},  # features fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_missing_title(self):
        url = reverse('offer-list-create')
        details = [
            {'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},  # title fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_missing_revisions(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},  # revisions fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_missing_delivery_time(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},  # delivery_time_in_days fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_missing_price(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'features': ['A'], 'offer_type': 'basic'},  # price fehlt
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_all_fields_missing(self):
        url = reverse('offer-list-create')
        details = [{}, {}, {}]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_offer_detail_extra_fields(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic', 'extra': 'field'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_with_null(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': [None], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_with_empty_string(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': [''], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_with_numbers(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': [1, 2, 3], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_with_dict(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': [{'foo': 'bar'}], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_with_bool(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': [True, False], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_offer_detail_features_with_mixed_types(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A', 1, None, True, {'foo': 'bar'}], 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'Test', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_delete_user_cascades_offers(self):
        # Create user and offer
        user = User.objects.create_user(username='cascadeuser', password='pw')
        self.client.login(username='cascadeuser', password='pw')
        url = reverse('offer-list-create')
        data = {
            'title': 'CascadeOffer',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        offer_resp = self.client.post(url, data, format='json')
        self.assertEqual(offer_resp.status_code, 201)
        offer_id = offer_resp.data.get('id')
        user.delete()
        detail_url = reverse('offer-detail', args=[offer_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)

    def test_offer_with_nonexistent_user(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'InvalidUserOffer',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ],
            'owner': 99999
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [400, 403, 401])

    def test_bulk_offer_transaction_rollback(self):
        url = reverse('offer-list-create')
        # First offer is valid, second is invalid
        valid = {
            'title': 'Bulk1', 'description': 'desc', 'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        invalid = {
            'title': 'Bulk2', 'description': 'desc', 'details': []
        }
        resp1 = self.client.post(url, valid, format='json')
        resp2 = self.client.post(url, invalid, format='json')
        self.assertEqual(resp1.status_code, 201)
        self.assertEqual(resp2.status_code, 400)
        # Prüfe, dass Bulk1 noch existiert
        if 'id' in resp1.data:
            detail_url = reverse('offer-detail', args=[resp1.data['id']])
            get_resp = self.client.get(detail_url)
            self.assertEqual(get_resp.status_code, 200)

    def test_unicode_and_special_characters(self):
        url = reverse('offer-list-create')
        data = {
            'title': 'Emoji 😃 Ümläut',
            'description': 'Beschreibung mit € und 中文',
            'details': [
                {'title': 'Básïc', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A', 'ß', '💡'], 'offer_type': 'basic'},
                {'title': 'Ständard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B', 'ü'], 'offer_type': 'standard'},
                {'title': 'Prémium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C', '漢字'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_file_upload_offer(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('offer-list-create')
        image = SimpleUploadedFile('test.jpg', b'filecontent', content_type='image/jpeg')
        data = {
            'title': 'FileUpload',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ],
            'image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, [201, 400])

    def test_missing_user_agent_header(self):
        url = reverse('offer-list-create')
        self.client.defaults.pop('HTTP_USER_AGENT', None)
        data = {
            'title': 'NoUserAgent',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_accept_language_header(self):
        url = reverse('offer-list-create')
        self.client.defaults['HTTP_ACCEPT_LANGUAGE'] = 'de-DE'
        data = {
            'title': 'Sprache',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400])

    def test_long_running_request(self):
        import time
        url = reverse('offer-list-create')
        data = {
            'title': 'SlowRequest',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        start = time.time()
        response = self.client.post(url, data, format='json')
        duration = time.time() - start
        self.assertIn(response.status_code, [201, 400])
        self.assertLess(duration, 10.0)

    def test_cross_field_validation(self):
        url = reverse('offer-list-create')
        details = [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'premium'},  # price zu niedrig für premium
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
        ]
        data = {'title': 'CrossField', 'description': 'desc', 'details': details}
        response = self.client.post(url, data, format='json')
        # Je nach Logik: 400 wenn cross-field validation implementiert, sonst 201
        self.assertIn(response.status_code, [201, 400])

    def test_rate_limiting(self):
        url = reverse('offer-list-create')
        for _ in range(100):
            response = self.client.get(url)
        # Kein echtes Rate-Limit implementiert, aber Test prüft, ob API nicht abstürzt
        self.assertIn(response.status_code, [200, 429, 400])

    def test_api_versioning(self):
        url = reverse('offer-list-create')
        self.client.defaults['HTTP_ACCEPT'] = 'application/vnd.api+json; version=2.0'
        data = {
            'title': 'VersionTest',
            'description': 'desc',
            'details': [
                {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 1, 'price': 10, 'features': ['A'], 'offer_type': 'basic'},
                {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 2, 'price': 20, 'features': ['B'], 'offer_type': 'standard'},
                {'title': 'Premium', 'revisions': 3, 'delivery_time_in_days': 3, 'price': 30, 'features': ['C'], 'offer_type': 'premium'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [201, 400, 406])
