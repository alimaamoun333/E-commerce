from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Category, Product

class CategoryAPITestCase(APITestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(name="Electronics", slug="electronics")
        self.cat2 = Category.objects.create(name="Books", slug="books")
        # products in cat1
        for i in range(5):
            Product.objects.create(title=f"Phone {i}", category=self.cat1, price=100 + i)
        self.list_url = reverse('category-list')

    def test_list_categories_contains_products_count(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # find electronics entry
        items = resp.json().get('results') or resp.json()
        found = [c for c in items if c['id'] == self.cat1.id][0]
        self.assertEqual(found['products_count'], 5)

    def test_retrieve_category_with_products_expanded(self):
        url = reverse('category-detail', args=[self.cat1.pk])
        resp = self.client.get(url + '?include_products=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.json().get('products')) == 5)

    def test_create_category_validation_duplicate_name(self):
        data = {'name': 'Electronics'}
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_blocked_if_has_products(self):
        url = reverse('category-detail', args=[self.cat1.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_with_delete_products_true(self):
        url = reverse('category-detail', args=[self.cat1.pk]) + '?delete_products=true'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.cat1.pk).exists())
        self.assertEqual(Product.objects.filter(category=self.cat1).count(), 0)

    def test_delete_with_reassign(self):
        url = reverse('category-detail', args=[self.cat1.pk]) + f'?reassign_to={self.cat2.pk}'
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # products moved
        self.assertEqual(Product.objects.filter(category=self.cat2).count(), 5)

    def test_filter_search_and_order(self):
        # search
        resp = self.client.get(self.list_url + '?search=Book')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        contents = resp.json().get('results') or resp.json()
        self.assertTrue(any('Books' in c['name'] for c in contents))
        # ordering by -products_count
        resp2 = self.client.get(self.list_url + '?ordering=-products_count')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        results = resp2.json().get('results') or resp2.json()
        if len(results) >= 2:
            self.assertTrue(results[0]['products_count'] >= results[1]['products_count'])
