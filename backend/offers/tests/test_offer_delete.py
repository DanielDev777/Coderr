from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile
from offers.models import Offer, OfferDetail

class OfferDeleteTests(APITestCase):
    """Test suite for DELETE /api/offers/<id>/ endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.owner)
        self.owner_token = Token.objects.create(user=self.owner)
        
        self.other_user = User.objects.create_user(
            username='other',
            password='pass456'
        )
        BusinessProfile.objects.create(user=self.other_user)
        self.other_token = Token.objects.create(user=self.other_user)
        
        self.offer = Offer.objects.create(
            user=self.owner,
            title='Test Offer',
            description='Test description'
        )
        
        for offer_type in ['basic', 'standard', 'premium']:
            OfferDetail.objects.create(
                offer=self.offer,
                title=f'{offer_type.capitalize()} Package',
                revisions=2,
                delivery_time_in_days=3,
                price='50.00',
                features=['Feature'],
                offer_type=offer_type
            )
    
    def test_owner_delete_offer(self):
        """Owner should successfully delete offer"""
        offer_id = self.offer.id
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')
        
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)
        
        response = self.client.delete(f'/api/offers/{offer_id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)
        
        self.assertEqual(Offer.objects.count(), 0)
        
        self.assertEqual(OfferDetail.objects.count(), 0)
    
    def test_non_owner_cannot_delete_offer(self):
        """Non-owner should get 403 Forbidden"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')
        
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        
        self.assertEqual(response.status_code, 403)
        
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)
    
    def test_unauthenticated_user_cannot_delete_offer(self):
        """User without token should get 401"""
        
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Offer.objects.count(), 1)
    
    def test_delete_nonexistent_offer(self):
        """Deleting non-existent offer should return 404"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')
        nonexistent_id = 99999
        
        response = self.client.delete(f'/api/offers/{nonexistent_id}/')
        
        self.assertEqual(response.status_code, 404)