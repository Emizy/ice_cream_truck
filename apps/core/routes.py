from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, UserViewSet, CompanyViewSet, FranchiseViewSet, TruckViewSet

router = DefaultRouter()
router.register(r'', RegisterViewSet, basename='api-register')
router.register(r'user', UserViewSet, basename='api-user')
router.register(r'company', CompanyViewSet, basename='api-company')
router.register(r'franchise', FranchiseViewSet, basename='api-franchise')
router.register(r'ice-cream-truck', TruckViewSet, basename='api-truck')
