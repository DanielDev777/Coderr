from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers.models import Offer, OfferDetail
from orders.models import Order
from users.models import BusinessProfile, CustomerProfile

class OrderUpdateTests(APITestCase):
    """Test suite for PATCH /api/orders/{id}/ endpoint"""
    
    def setUp(self):
        """Create test users and order"""
        self.business_user1 = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user1)
        self.biz1_token = Token.objects.create(user=self.business_user1)
        
        self.business_user2 = User.objects.create_user(
            username='business2',
            password='pass456'
        )
        BusinessProfile.objects.create(user=self.business_user2)
        self.biz2_token = Token.objects.create(user=self.business_user2)
        
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass789'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        
        self.offer = Offer.objects.create(
            user=self.business_user1,
            title='Logo Design',
            description='Professional logo'
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Logo',
            revisions=2,
            delivery_time_in_days=3,
            price='50.00',
            features=['1 Concept'],
            offer_type='basic'
        )
        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user1,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
            status='in_progress'
        )
    
    def test_business_user_can_update_status(self):
        """Business user should be able to update order status"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.biz1_token.key}')
        data = {'status': 'completed'}
        
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')
    
    def test_customer_cannot_update_status(self):
        """Customer user should not be able to update order"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {'status': 'completed'}
        
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 403)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')
    
    def test_non_related_business_user_cannot_update(self):
        """Different business user should get 404 (order filtered from queryset)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.biz2_token.key}')
        data = {'status': 'completed'}
        
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 404)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')
    
    def test_invalid_status_returns_400(self):
        """Invalid status value should return 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.biz1_token.key}')
        data = {'status': 'invalid_status'}
        
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_unauthenticated_user_cannot_update(self):
        """User without token should get 401"""
        data = {'status': 'completed'}
        
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_only_status_field_updatable(self):
        """Should only allow updating status field"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.biz1_token.key}')
        original_price = self.order.price
        
        data = {
            'status': 'completed',
            'price': '999.99'
        }
        
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')
        self.assertEqual(self.order.price, Decimal('50.00'))