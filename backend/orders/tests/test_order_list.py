from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from offers.models import Offer, OfferDetail
from orders.models import Order

class OrderListTests(APITestCase):
    """Test suite for GET /api/orders/ endpoint"""

    def setUp(self):
        self.business_user1 = User.objects.create_user(
            username='biz1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user1)
        self.biz1_token = Token.objects.create(user=self.business_user1)
        
        self.business_user2 = User.objects.create_user(
            username='biz2',
            password='pass456'
        )
        BusinessProfile.objects.create(user=self.business_user2)
        self.biz2_token = Token.objects.create(user=self.business_user2)
        
        self.customer_user1 = User.objects.create_user(
            username='cust1',
            password='pass789'
        )
        CustomerProfile.objects.create(user=self.customer_user1)
        self.cust1_token = Token.objects.create(user=self.customer_user1)
        
        self.customer_user2 = User.objects.create_user(
            username='cust2',
            password='pass000'
        )
        CustomerProfile.objects.create(user=self.customer_user2)
        self.cust2_token = Token.objects.create(user=self.customer_user2)
        
        self.offer1 = Offer.objects.create(
            user=self.business_user1,
            title='Logo Design',
            description='Professional logo'
        )
        self.detail1 = OfferDetail.objects.create(
            offer=self.offer1,
            title='Basic Logo',
            revisions=2,
            delivery_time_in_days=3,
            price='50.00',
            features=['1 Concept', 'PNG File'],
            offer_type='basic'
        )
        
        self.offer2 = Offer.objects.create(
            user=self.business_user2,
            title='Website Design',
            description='Modern website'
        )
        self.detail2 = OfferDetail.objects.create(
            offer=self.offer2,
            title='Standard Website',
            revisions=5,
            delivery_time_in_days=7,
            price='500.00',
            features=['5 Pages', 'Responsive'],
            offer_type='standard'
        )
        
        self.order1 = Order.objects.create(
            customer_user=self.customer_user1,
            business_user=self.business_user1,
            offer_detail=self.detail1,
            title=self.detail1.title,
            revisions=self.detail1.revisions,
            delivery_time_in_days=self.detail1.delivery_time_in_days,
            price=self.detail1.price,
            features=self.detail1.features,
            offer_type=self.detail1.offer_type,
            status='in_progress'
        )
        
        self.order2 = Order.objects.create(
            customer_user=self.customer_user1,
            business_user=self.business_user2,
            offer_detail=self.detail2,
            title=self.detail2.title,
            revisions=self.detail2.revisions,
            delivery_time_in_days=self.detail2.delivery_time_in_days,
            price=self.detail2.price,
            features=self.detail2.features,
            offer_type=self.detail2.offer_type,
            status='completed'
        )
        
        self.order3 = Order.objects.create(
            customer_user=self.customer_user2,
            business_user=self.business_user1,
            offer_detail=self.detail1,
            title=self.detail1.title,
            revisions=self.detail1.revisions,
            delivery_time_in_days=self.detail1.delivery_time_in_days,
            price=self.detail1.price,
            features=self.detail1.features,
            offer_type=self.detail1.offer_type,
            status='in_progress'
        )

    def test_customer_list_their_orders(self):
        """Customer should see only orders they placed"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cust1_token.key}')
        
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2) 

        order_ids = [order['id'] for order in response.data['results']]
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order2.id, order_ids)
        self.assertNotIn(self.order3.id, order_ids)

    def test_business_user_list_their_orders(self):
        """Business user should see orders for their services"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.biz1_token.key}')
        
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        
        order_ids = [order['id'] for order in response.data['results']]
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order3.id, order_ids)
        self.assertNotIn(self.order2.id, order_ids)
    
    def test_user_sees_orders_from_both_roles(self):
        """User who is both customer and business should see all related orders"""
        Order.objects.create(
            customer_user=self.business_user1,
            business_user=self.business_user2,
            offer_detail=self.detail2,
            title=self.detail2.title,
            revisions=self.detail2.revisions,
            delivery_time_in_days=self.detail2.delivery_time_in_days,
            price=self.detail2.price,
            features=self.detail2.features,
            offer_type=self.detail2.offer_type,
            status='in_progress'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.biz1_token.key}')
        
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

    def test_unauthenticated_user_cannot_list_orders(self):
        """User without token should get 401"""
        
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_order_fields_in_response(self):
        """Response should contain all expected fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cust1_token.key}')
        
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        order = response.data['results'][0]
        
        self.assertIn('id', order)
        self.assertIn('customer_user', order)
        self.assertIn('business_user', order)
        self.assertIn('title', order)
        self.assertIn('revisions', order)
        self.assertIn('delivery_time_in_days', order)
        self.assertIn('price', order)
        self.assertIn('features', order)
        self.assertIn('offer_type', order)
        self.assertIn('status', order)
        self.assertIn('created_at', order)
        self.assertIn('updated_at', order)