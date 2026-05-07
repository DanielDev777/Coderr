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

    def test_customer_login_user(self):
        data = {
            'username': 'custuser',
            'password': 'pass456',
        }
        response = self.client.post('/api/login/', data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'custuser')
        self.assertEqual(response.data['type'], 'customer')

    def test_customer_login_user_invalid_password(self):
        """Test login with wrong password returns 400"""
        data = {
            'username': 'custuser',
            'password': 'wrongpassword',
        }
        response = self.client.post('/api/login/', data)

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)
        self.assertIn('non_field_errors', response.data)

    def test_customer_login_user_missing_username(self):
        """Test login without username returns 400"""
        data = {
            'password': 'pass456',
        }
        response = self.client.post('/api/login/', data)

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)
        self.assertIn('username', response.data)

    def test_customer_login_user_missing_password(self):
        """Test login without password returns 400"""
        data = {
            'username': 'custuser',
        }
        response = self.client.post('/api/login/', data)

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)
        self.assertIn('password', response.data)
