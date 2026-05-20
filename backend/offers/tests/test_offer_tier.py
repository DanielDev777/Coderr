from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile
from offers.models import Offer, OfferDetail
from decimal import Decimal

class OfferTierDetailTests(APITestCase):
    """Test suite for GET /api/offerdetails/<id>/ endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        
        self.offer = Offer.objects.create(
            user=self.user,
            title='Test Offer',
            description='Test'
        )
        
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Package',
            revisions=5,
            delivery_time_in_days=5,
            price='150.00',
            features=['Feature 1', 'Feature 2', 'Feature 3'],
            offer_type='standard'
        )
    
    def test_authenticated_user_retrieve_offerdetail(self):
        """Authenticated user should retrieve detail successfully"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.get(f'/api/offerdetails/{self.detail.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.detail.id)
        self.assertEqual(response.data['title'], 'Standard Package')
        self.assertEqual(response.data['revisions'], 5)
        self.assertEqual(response.data['delivery_time_in_days'], 5)
        self.assertEqual(float(response.data['price']), 150.00)
        self.assertEqual(response.data['offer_type'], 'standard')
        self.assertEqual(len(response.data['features']), 3)
    
    def test_unauthenticated_user_cannot_retrieve_offerdetail(self):
        """User without token should get 401"""
        
        response = self.client.get(f'/api/offerdetails/{self.detail.id}/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_retrieve_nonexistent_offerdetail(self):
        """Requesting non-existent detail should return 404"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        nonexistent_id = 99999
        
        response = self.client.get(f'/api/offerdetails/{nonexistent_id}/')
        
        self.assertEqual(response.status_code, 404)