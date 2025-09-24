# products/api/views.py
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from products.models import Category, Product
from .serializers import CategorySerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().annotate(products_count=Count('products'))
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'slug']                    # simple exact filters
    search_fields = ['name', 'description']                # full-text-ish search
    ordering_fields = ['name', 'created_at', 'products_count']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # annotate products_count (ensure present if not)
        qs = Category.objects.all().annotate(products_count=Count('products'))
        # optional filtering by min_products / max_products
        request = self.request
        minp = request.query_params.get('min_products')
        maxp = request.query_params.get('max_products')
        if minp is not None:
            try:
                minp = int(minp)
                qs = qs.filter(products_count__gte=minp)
            except ValueError:
                pass
        if maxp is not None:
            try:
                maxp = int(maxp)
                qs = qs.filter(products_count__lte=maxp)
            except ValueError:
                pass
        return qs

    def destroy(self, request, *args, **kwargs):
        """
        Delete behavior:
          - Default: if category has products -> 400 (prevent accidental data loss).
          - If ?delete_products=true -> deletes products in that category then deletes category.
          - If ?reassign_to=<category_id> -> reassigns products to that category then deletes this category.
        """
        instance = self.get_object()
        products_qs = instance.products.all()
        count = products_qs.count()

        delete_products = request.query_params.get('delete_products', 'false').lower() in ('1','true','yes')
        reassign_to = request.query_params.get('reassign_to')

        if count == 0:
            return super().destroy(request, *args, **kwargs)

        if delete_products:
            products_qs.delete()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if reassign_to is not None:
            try:
                new_cat = Category.objects.get(pk=int(reassign_to))
            except (ValueError, Category.DoesNotExist):
                return Response({"detail": "Invalid reassign_to category id."}, status=status.HTTP_400_BAD_REQUEST)
            # reassign
            products_qs.update(category=new_cat)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            "detail": "Category contains products. Use ?delete_products=true to delete products, or ?reassign_to=<id> to move products before deletion."
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='products', url_name='category-products')
    def list_products(self, request, pk=None):
        """
        Extra endpoint: /categories/{pk}/products/ to list products belonging to a category.
        Accepts pagination, ordering, filtering via query params if desired.
        """
        category = self.get_object()
        qs = category.products.all()
        # simple pagination using view's pagination_class
        page = self.paginate_queryset(qs)
        from products.api.serializers import ProductBriefSerializer
        if page is not None:
            serializer = ProductBriefSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ProductBriefSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
