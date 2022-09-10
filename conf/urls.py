from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from apps.core import routes as core_router
from apps.store import routes as store_router
from apps.orders import routes as order_router
from apps.core.views import account_logout

schema_view = get_schema_view(
    openapi.Info(
        title="ICE CREAM TRUCK API",
        default_version="v1",
        description="Endpoints showing interactable part of the system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    authentication_classes=(SessionAuthentication, JWTAuthentication),
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'accounts/logout/', account_logout),
    path("api/v1/", include(core_router.router.urls)),
    path("api/v1/store/", include(store_router.router.urls)),
    path("api/v1/order/", include(order_router.router.urls)),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("",
         schema_view.with_ui("swagger", cache_timeout=0),
         name="schema-swagger-ui",
         ),
]
