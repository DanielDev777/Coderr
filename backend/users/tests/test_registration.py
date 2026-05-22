from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from users.models import BusinessProfile, CustomerProfile


class RegistrationTests(APITestCase):
    def test_register_business_user(self):
        """Test successful business user registration"""
        data = {
            'username': 'bizuser',
            'email': 'biz@test.com',
            'password': 'pass123',
            'repeated_password': 'pass123',
            'type': 'business'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'bizuser')
        self.assertEqual(response.data['email'], 'biz@test.com')
        self.assertEqual(response.data['type'], 'business')
        
        user = User.objects.get(username='bizuser')
        self.assertEqual(user.email, 'biz@test.com')
        self.assertTrue(BusinessProfile.objects.filter(user=user).exists())
    
    def test_register_customer_user(self):
        """Test successful customer user registration"""
        data = {
            'username': 'custuser',
            'email': 'cust@test.com',
            'password': 'pass456',
            'repeated_password': 'pass456',
            'type': 'customer'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['type'], 'customer')
        
        user = User.objects.get(username='custuser')
        self.assertTrue(CustomerProfile.objects.filter(user=user).exists())
    
    def test_register_duplicate_username(self):
        """Test registration with existing username returns 400"""
        User.objects.create_user(username='existing', password='pass123')
        
        data = {
            'username': 'existing',
            'email': 'new@test.com',
            'password': 'pass123',
            'repeated_password': 'pass123',
            'type': 'business'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
    
    def test_register_missing_username(self):
        """Test registration without username returns 400"""
        data = {
            'email': 'test@test.com',
            'password': 'pass123',
            'type': 'business'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
    
    def test_register_missing_password(self):
        """Test registration without password returns 400"""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'type': 'business'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
    
    def test_register_missing_type(self):
        """Test registration without type returns 400"""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'pass123'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('type', response.data)
    
    def test_register_invalid_type(self):
        """Test registration with invalid type returns 400"""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'pass123',
            'type': 'invalid_type'
        }
        response = self.client.post('/api/registration/', data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('type', response.data)