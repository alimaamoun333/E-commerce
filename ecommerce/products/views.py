import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsOwnerOrStaffOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet providing list/retrieve/create/update/destroy for Product.
    Uses select_related to optimize queries for owner and category.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]  # object-level permission included
    queryset = Product.objects.select_related('owner', 'category').all()

    def get_permissions(self):
        # keep default behavior but ensure read-only for unauthenticated
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        try:
            instance = serializer.save(owner=self.request.user)
            logger.info("Product created: id=%s owner=%s", instance.id, self.request.user)
        except Exception as e:
            logger.exception("Failed to create product for user=%s: %s", self.request.user, str(e))
            raise

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.exception("Create product error: %s", e)
            # Return validation errors or a 400 with detail
            return Response({'detail': str(e)}, status=getattr(e, 'status_code', status.HTTP_400_BAD_REQUEST))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # raises 404 if not found
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info("Product updated: id=%s user=%s", instance.id, request.user)
            return Response(serializer.data)
        except Exception as e:
            logger.exception("Update product error: %s", e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            logger.info("Product deleted: id=%s by user=%s", instance.id, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception("Delete product error: %s", e)
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Optionally filter out inactive products for anonymous users, etc.
        qs = Product.objects.select_related('owner', 'category').all()
        # Example filter: non-staff see only active products
        if not (self.request.user.is_staff if self.request.user.is_authenticated else False):
            qs = qs.filter(is_active=True)
        return qs
