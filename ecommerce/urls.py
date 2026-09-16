from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'variants', views.ProductVariantViewSet, basename='variant')

urlpatterns = [
    path('auth/register/', views.register_user, name='register'),
    path('', include(router.urls)),
]