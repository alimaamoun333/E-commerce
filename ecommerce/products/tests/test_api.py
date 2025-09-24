from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ..models import Product, Category

User = get_user_model()

class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password='pass123')
        self.other_user = User.objects.create_user(username='user2', password='pass123')
        self.staff = User.objects.create_user(username='staff', password='pass123', is_staff=True)
        self.category = Category.objects.create(name='Default')

        self.product = Product.objects.create(
            owner=self.user,
            category=self.category,
            name='Test Product',
            description='A product for testing',
            price='9.99',
            stock=10,
            is_active=True
        )

        self.list_url = reverse('product-list')  # router naming: product-list
        self.detail_url = lambda pk: reverse('product-detail', args=[pk])

    def test_list_products_anonymous(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # pagination keys present
        self.assertIn('results', resp.data)

    def test_retrieve_product(self):
        resp = self.client.get(self.detail_url(self.product.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Test Product')

    def test_create_product_requires_auth(self):
        data = {
            'name': 'New P',
            'description': 'desc',
            'price': '5.00',
            'stock': 1,
            'category': self.category.id
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # authenticated
        self.client.force_authenticate(self.user)
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['owner'], self.user.username)

    def test_update_product_owner_only(self):
        url = self.detail_url(self.product.id)
        data = {'name': 'Updated name', 'price': '19.99', 'stock': 5}
        # other user cannot update
        self.client.force_authenticate(self.other_user)
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # owner can update
        self.client.force_authenticate(self.user)
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated name')

        # staff can update others
        self.client.force_authenticate(self.staff)
        resp = self.client.patch(url, {'name': 'Staff changed'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_product_owner_or_staff(self):
        url = self.detail_url(self.product.id)
        # other user can't delete
        self.client.force_authenticate(self.other_user)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # owner can delete
        self.client.force_authenticate(self.user)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_validation_errors(self):
        self.client.force_authenticate(self.user)
        data = {'name': 'x', 'price': '-1.00', 'stock': -5}
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Expect errors for name, price, stock
        self.assertIn('name', resp.data)
        self.assertIn('price', resp.data)
        self.assertIn('stock', resp.data)

    def test_pagination(self):
        # create many products
        self.client.force_authenticate(self.user)
        for i in range(25):
            Product.objects.create(
                owner=self.user,
                category=self.category,
                name=f'P{i}',
                description='x',
                price='1.00',
                stock=1
            )
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # default page size set to 10 in settings example
        self.assertIn('results', resp.data)
        self.assertTrue(len(resp.data['results']) <= 12)  # depending on pagination settings
