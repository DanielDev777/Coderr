from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from offers.models import Offer, OfferDetail
from orders.models import Order


class OrderCreateTests(APITestCase):
    """Test suite for POST /api/orders/ endpoint"""

    def setUp(self):
        """Create test users and offer"""
        self.business_user = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)
        self.business_token = Token.objects.create(user=self.business_user)
        
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass456'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Website Development',
            description='Full-stack development'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Package',
            revisions=5,
            delivery_time_in_days=14,
            price='999.99',
            features=['Frontend', 'Backend', 'Database', 'Hosting'],
            offer_type='premium'
        )
    
    def test_customer_can_create_order(self):
        """Customer user should successfully create order"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.customer_user, self.customer_user)
        self.assertEqual(order.business_user, self.business_user)
        self.assertEqual(order.offer_detail, self.detail)
    
    def test_business_user_cannot_create_order(self):
        """Business users should not be able to create orders"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.count(), 0)
    
    def test_invalid_offer_detail_id_returns_400(self):
        """Invalid offer_detail_id should return 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'offer_detail_id': 9999}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('offer_detail_id', response.data)
    
    def test_customer_and_business_user_auto_set(self):
        """customer_user and business_user should be set automatically"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        
        order = Order.objects.first()
        self.assertEqual(order.customer_user.id, self.customer_user.id)
        self.assertEqual(order.business_user.id, self.business_user.id)
    
    def test_all_fields_copied_from_offer_detail(self):
        """All OfferDetail fields should be copied to Order"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        
        order = Order.objects.first()
        self.assertEqual(order.title, self.detail.title)
        self.assertEqual(order.revisions, self.detail.revisions)
        self.assertEqual(order.delivery_time_in_days, self.detail.delivery_time_in_days)
        self.assertEqual(order.price, self.detail.price)
        self.assertEqual(order.features, self.detail.features)
        self.assertEqual(order.offer_type, self.detail.offer_type)
        
        self.assertEqual(order.status, 'in_progress')
    
    def test_snapshot_pattern_price_preserved(self):
        """Order price should remain unchanged if OfferDetail price changes"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        order = Order.objects.first()
        original_price = order.price
        
        self.detail.price = '1500.00'
        self.detail.save()
        
        order.refresh_from_db()
        self.assertEqual(order.price, original_price)
        self.assertNotEqual(order.price, self.detail.price)
    
    def test_unauthenticated_user_cannot_create_order(self):
        """User without token should get 401"""
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 401)
    
    def test_response_contains_all_fields(self):
        """Response should include all order fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'offer_detail_id': self.detail.id}
        
        response = self.client.post('/api/orders/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        
        self.assertIn('id', response.data)
        self.assertIn('customer_user', response.data)
        self.assertIn('business_user', response.data)
        self.assertIn('title', response.data)
        self.assertIn('price', response.data)
        self.assertIn('status', response.data)