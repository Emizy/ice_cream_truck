from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, FlavorViewSet

router = DefaultRouter()
router.register(r'store', StoreViewSet, basename='api-store')
router.register(r'flavor', FlavorViewSet, basename='api-flavor')
