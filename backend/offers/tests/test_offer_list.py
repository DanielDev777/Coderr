from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from offers.models import Offer, OfferDetail
from users.models import BusinessProfile
from decimal import Decimal
import time


class OfferListTests(APITestCase):
    def setUp(self):
        """Create test users and offers"""
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        BusinessProfile.objects.create(user=self.user1)
        
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        BusinessProfile.objects.create(user=self.user2)

    def create_offer_with_details(self, user, title, description='Test description', 
                                   basic_price=100, standard_price=200, premium_price=300,
                                   basic_days=14, standard_days=7, premium_days=3):
        """Helper to create an offer with 3 details"""
        offer = Offer.objects.create(
            user=user,
            title=title,
            description=description
        )
        
        OfferDetail.objects.create(
            offer=offer,
            title='Basic',
            revisions=1,
            delivery_time_in_days=basic_days,
            price=Decimal(str(basic_price)),
            features=['feature1'],
            offer_type='basic'
        )
        OfferDetail.objects.create(
            offer=offer,
            title='Standard',
            revisions=2,
            delivery_time_in_days=standard_days,
            price=Decimal(str(standard_price)),
            features=['feature1', 'feature2'],
            offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=offer,
            title='Premium',
            revisions=3,
            delivery_time_in_days=premium_days,
            price=Decimal(str(premium_price)),
            features=['feature1', 'feature2', 'feature3'],
            offer_type='premium'
        )
        
        return offer

    def test_unauthenticated_user_can_access_offer_list(self):
        """Test that unauthenticated users can view offer list"""
        self.create_offer_with_details(self.user1, 'Test Offer')
        
        response = self.client.get('/api/offers/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_offer_list_pagination(self):
        """Test that pagination works with PAGE_SIZE=6"""
        for i in range(8):
            self.create_offer_with_details(self.user1, f'Offer {i}')
        
        response = self.client.get('/api/offers/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 8)
        self.assertEqual(len(response.data['results']), 6)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_filter_by_creator_id(self):
        """Test filtering offers by creator_id"""
        self.create_offer_with_details(self.user1, 'User1 Offer')
        self.create_offer_with_details(self.user2, 'User2 Offer')
        
        response = self.client.get(f'/api/offers/?creator_id={self.user1.id}')
        
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user'], self.user1.id)
        self.assertEqual(results[0]['title'], 'User1 Offer')

    def test_filter_by_max_delivery_time(self):
        """Test filtering by max_delivery_time"""
        self.create_offer_with_details(
            self.user1, 'Fast Offer',
            basic_days=5, standard_days=3, premium_days=1
        )
        self.create_offer_with_details(
            self.user1, 'Slow Offer',
            basic_days=30, standard_days=20, premium_days=10
        )
        
        response = self.client.get('/api/offers/?max_delivery_time=7')
        
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Fast Offer')
        self.assertLessEqual(results[0]['min_delivery_time'], 7)

    def test_search_in_title_and_description(self):
        """Test search functionality in title and description"""
        self.create_offer_with_details(self.user1, 'Logo Design', 'Professional logo')
        self.create_offer_with_details(self.user1, 'Web Development', 'Build websites')
        self.create_offer_with_details(self.user1, 'Mobile App', 'Design mobile apps')
        
        response = self.client.get('/api/offers/?search=Design')
        
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        titles = [r['title'] for r in results]
        self.assertIn('Logo Design', titles)
        self.assertIn('Mobile App', titles)

    def test_ordering_by_updated_at(self):
        """Test ordering by updated_at field"""
        offer1 = self.create_offer_with_details(self.user1, 'Offer 1')
        time.sleep(0.01)
        offer2 = self.create_offer_with_details(self.user1, 'Offer 2')
        time.sleep(0.01)
        offer3 = self.create_offer_with_details(self.user1, 'Offer 3')
        
        response = self.client.get('/api/offers/?ordering=-updated_at')
        
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Offer 3')
        self.assertEqual(results[1]['title'], 'Offer 2')
        self.assertEqual(results[2]['title'], 'Offer 1')

    def test_ordering_by_min_price(self):
        """Test ordering by min_price"""
        self.create_offer_with_details(
            self.user1, 'Expensive',
            basic_price=500, standard_price=800, premium_price=1200
        )
        self.create_offer_with_details(
            self.user1, 'Cheap',
            basic_price=50, standard_price=100, premium_price=150
        )
        self.create_offer_with_details(
            self.user1, 'Medium',
            basic_price=200, standard_price=300, premium_price=400
        )
        
        response = self.client.get('/api/offers/?ordering=min_price')
        
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Cheap')
        self.assertEqual(results[1]['title'], 'Medium')
        self.assertEqual(results[2]['title'], 'Expensive')

    def test_min_price_and_min_delivery_time_computed(self):
        """Test that min_price and min_delivery_time are correctly computed"""
        self.create_offer_with_details(
            self.user1, 'Test Offer',
            basic_price=150, standard_price=250, premium_price=400,
            basic_days=10, standard_days=5, premium_days=2
        )
        
        response = self.client.get('/api/offers/')
        
        self.assertEqual(response.status_code, 200)
        offer_data = response.data['results'][0]
        
        self.assertEqual(offer_data['min_price'], 150)
        self.assertEqual(offer_data['min_delivery_time'], 2)

    def test_empty_results(self):
        """Test that empty results are handled correctly"""
        response = self.client.get('/api/offers/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)