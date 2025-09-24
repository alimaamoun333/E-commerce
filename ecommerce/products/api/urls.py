from rest_framework.routers import DefaultRouter
from products.api.views import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = router.urls
