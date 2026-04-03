from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from api import views


app_name = "api"

router = DefaultRouter()
router.register(r"assets", views.AssetViewSet, basename="asset")
router.register(r"work-orders", views.WorkOrderViewSet, basename="work-order")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path("", include(router.urls)),
]