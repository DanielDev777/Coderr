from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile
from offers.models import Offer, OfferDetail


class OfferDetailTests(APITestCase):
    def setUp(self):
        """Create test user and offer"""
        self.user = User.objects.create_user(
            username='bizuser',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)

        self.offer = Offer.objects.create(
            user=self.user,
            title='Test Offer',
            description='Test description'
        )

        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=3,
            price='50.00',
            features=['Feature 1'],
            offer_type='basic'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=5,
            price='150.00',
            features=['Feature 1', 'Feature 2'],
            offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=7,
            price='300.00',
            features=['Feature 1', 'Feature 2', 'Feature 3'],
            offer_type='premium'
        )

    def test_authenticated_user_retrieve_offer(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.get(f'/api/offers/{self.offer.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.offer.id)
        self.assertEqual(response.data['title'], 'Test Offer')
        self.assertEqual(len(response.data['details']), 3)
        self.assertEqual(response.data['min_price'], 50.0)
        self.assertEqual(response.data['min_delivery_time'], 3)

    def test_unauthenticated_user_cannot_retrieve_offer(self):
        """Unauthenticated user should get 401"""

        response = self.client.get(f'/api/offers/{self.offer.id}/')

        self.assertEqual(response.status_code, 401)

    def test_retrieve_nonexistent_offer(self):
        """Requesting non-existent offer should return 404"""

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        nonexistent_id = 99999

        response = self.client.get(f'/api/offers/{nonexistent_id}/')

        self.assertEqual(response.status_code, 404)