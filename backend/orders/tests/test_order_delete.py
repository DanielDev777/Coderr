from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from offers.models import Offer, OfferDetail
from orders.models import Order


class OrderDeleteTests(APITestCase):
    """Test suite for DELETE /api/orders/{id}/ endpoint"""

    def setUp(self):
        """Create test users and order"""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

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
            business_user=self.business_user,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
            status='in_progress'
        )

    def test_admin_can_delete_order(self):
        """Admin user should be able to delete any order"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        order_id = self.order.id

        response = self.client.delete(f'/api/orders/{order_id}/')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Order.objects.count(), 0)
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_customer_cannot_delete_order(self):
        """Customer user should not be able to delete order"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        order_id = self.order.id

        response = self.client.delete(f'/api/orders/{order_id}/')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.count(), 1)
        self.assertTrue(Order.objects.filter(id=order_id).exists())

    def test_business_user_cannot_delete_order(self):
        """Business user should not be able to delete order"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        order_id = self.order.id

        response = self.client.delete(f'/api/orders/{order_id}/')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.count(), 1)

    def test_unauthenticated_user_cannot_delete(self):
        """User without token should get 401"""
        order_id = self.order.id

        response = self.client.delete(f'/api/orders/{order_id}/')

        self.assertEqual(response.status_code, 401)
