from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'variants', views.ProductVariantViewSet, basename='variant')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'wishlist', views.WishlistItemViewSet, basename='wishlist')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('auth/register/', views.register_user, name='register'),
    path('', include(router.urls)),
]