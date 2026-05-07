from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import BusinessProfile, CustomerProfile

class LoginTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='bizuser',
            email='biz@test.com',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)
        
        self.customer_user = User.objects.create_user(
            username='custuser',
            email='cust@test.com',
            password='pass456'
        )
        CustomerProfile.objects.create(user=self.customer_user)
    
    def test_login_business_user(self):
        data = {
            'username': 'bizuser',
            'password': 'pass123'
        }
        response = self.client.post('/api/login/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'bizuser')
        self.assertEqual(response.data['type'], 'business')