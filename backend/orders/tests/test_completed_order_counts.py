from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from offers.models import Offer, OfferDetail
from orders.models import Order


class CompletedOrderCountTests(APITestCase):
    """Test suite for GET /api/completed-order-count/{business_user_id}/ endpoint"""

    def setUp(self):
        """Create test users and orders (same as OrderCountTests)"""
        # Business user
        self.business_user = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)

        # Customer user
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass456'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

        # Create offer
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

        # Create orders: 2 in_progress, 3 completed, 1 cancelled
        for _ in range(2):
            Order.objects.create(
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

        for _ in range(3):
            Order.objects.create(
                customer_user=self.customer_user,
                business_user=self.business_user,
                offer_detail=self.detail,
                title=self.detail.title,
                revisions=self.detail.revisions,
                delivery_time_in_days=self.detail.delivery_time_in_days,
                price=self.detail.price,
                features=self.detail.features,
                offer_type=self.detail.offer_type,
                status='completed'
            )

        Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
            status='cancelled'
        )

    def test_returns_correct_completed_order_count(self):
        """Should return count of completed orders only"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')

        response = self.client.get(
            f'/api/completed-order-count/{self.business_user.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['completed_order_count'], 3)

    def test_returns_zero_when_no_completed_orders(self):
        """Should return 0 if business user has no completed orders"""
        new_business = User.objects.create_user(
            username='newbiz', password='pass')
        BusinessProfile.objects.create(user=new_business)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')

        response = self.client.get(
            f'/api/completed-order-count/{new_business.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['completed_order_count'], 0)

    def test_non_existent_user_returns_404(self):
        """Should return 404 for non-existent user"""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')

        response = self.client.get('/api/completed-order-count/9999/')

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_access(self):
        """User without token should get 401"""
        response = self.client.get(
            f'/api/completed-order-count/{self.business_user.id}/'
        )

        self.assertEqual(response.status_code, 401)
