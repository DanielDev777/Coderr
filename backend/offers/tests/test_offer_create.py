from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from offers.models import Offer, OfferDetail


class OfferCreateTests(APITestCase):
    def setUp(self):
        """Create test users and tokens before each test"""
        self.business_user = User.objects.create_user(
            username='businessuser',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)
        self.business_token = Token.objects.create(user=self.business_user)

        self.customer_user = User.objects.create_user(
            username='customeruser',
            password='pass123'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

    def get_valid_offer_data(self):
        """Helper method to get valid offer data - reusable across tests"""
        return {
            'title': 'Web Development',
            'description': 'Professional website',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 1,
                    'delivery_time_in_days': 7,
                    'price': 100,
                    'features': ['Homepage'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard',
                    'revisions': 3,
                    'delivery_time_in_days': 5,
                    'price': 200,
                    'features': ['Homepage', 'About'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium',
                    'revisions': 5,
                    'delivery_time_in_days': 3,
                    'price': 300,
                    'features': ['Homepage', 'About', 'Contact'],
                    'offer_type': 'premium'
                }
            ]
        }

    def test_business_user_can_create_offer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        
        data = self.get_valid_offer_data()

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertEqual(Offer.objects.count(), 1)

        offer = Offer.objects.first()
        self.assertEqual(offer.details.count(), 3)
        self.assertEqual(offer.user, self.business_user)
        self.assertEqual(offer.title, 'Web Development')

    def test_customer_user_cannot_create_offer(self):
        """Test that customer users are forbidden from creating offers"""

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')

        data = self.get_valid_offer_data()

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Offer.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_offer(self):
        data = self.get_valid_offer_data()

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Offer.objects.count(), 0)

    def test_less_than_three_details_returns_400(self):
        """Test that offers must have exactly 3 details"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        data = self.get_valid_offer_data()
        data['details'] = data['details'][:2]

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('details', response.data)
        self.assertEqual(Offer.objects.count(), 0)

    def test_more_than_three_details_returns_400(self):
        """Test that offers cannot have more than 3 details"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')

        data = self.get_valid_offer_data()
        data['details'].append({
            'title': 'Extra',
            'revisions': 10,
            'delivery_time_in_days': 1,
            'price': 500,
            'features': ['Everything'],
            'offer_type': 'extra'
        })

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Offer.objects.count(), 0)

    def test_duplicate_offer_type_returns_400(self):
        """Test that all 3 details must have different offer_types"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')

        data = self.get_valid_offer_data()
        data['details'][1]['offer_type'] = 'basic'

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('details', response.data)
        self.assertEqual(Offer.objects.count(), 0)

    def test_missing_title_returns_400(self):
        """Test that title field is required"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')

        data = self.get_valid_offer_data()
        del data['title']

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_creator_is_set_from_request_user(self):
        """Test that creator is automatically set from authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')

        data = self.get_valid_offer_data()
        data['user'] = 999

        response = self.client.post('/api/offers/', data, format='json')

        self.assertEqual(response.status_code, 201)
    
        offer = Offer.objects.first()
        self.assertEqual(offer.user, self.business_user)
        self.assertNotEqual(offer.user.id, 999)