from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile
from offers.models import Offer, OfferDetail
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile


class OfferUpdateTests(APITestCase):
    """Test suite for PATCH /api/offers/<id>/ endpoint"""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.owner)
        self.owner_token = Token.objects.create(user=self.owner)
        self.other_user = User.objects.create_user(
            username='other',
            password='pass456'
        )
        BusinessProfile.objects.create(user=self.other_user)
        self.other_token = Token.objects.create(user=self.other_user)
        self.offer = Offer.objects.create(
            user=self.owner,
            title='Original Title',
            description='Original description'
        )
        self.basic_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=3,
            price='50.00',
            features=['Feature 1'],
            offer_type='basic'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=5,
            price='150.00',
            features=['Feature 1', 'Feature 2'],
            offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=7,
            price='300.00',
            features=['Feature 1', 'Feature 2', 'Feature 3'],
            offer_type='premium'
        )

    def test_owner_update_offer_title(self):
        data = {'title': 'Updated Title'}
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated Title')

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Updated Title')
        self.assertEqual(self.offer.description, 'Original description')

    def test_owner_update_offer_description(self):
        data = {'description': 'Updated description'}
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.description, 'Updated description')
        self.assertEqual(self.offer.title, 'Original Title')

    def test_owner_update_detail_price(self):
        data = {
            'details': [
                {
                    'id': self.basic_detail.id,
                    'price': '75.00',
                    'offer_type': 'basic'
                }
            ]
        }
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.basic_detail.refresh_from_db()
        self.assertEqual(self.basic_detail.price, Decimal('75.00'))

    def test_non_owner_cannot_update_offer(self):
        data = {'title': 'Hacked Title'}
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.other_token.key}')

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 403)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Original Title')

    def test_unauthenticated_user_cannot_update_offer(self):
        data = {'title': 'Hacked Title'}
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_owner_upload_image(self):
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        data = {'image': image}
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.owner_token.key}')
        
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        self.offer.refresh_from_db()
        self.assertIsNotNone(self.offer.image)