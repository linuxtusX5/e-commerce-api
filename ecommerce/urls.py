from django.urls import path, include
# from rest_framework.router import DefaultRouter
from . import views

# router = DefaultRouter()
# router = register(r'register_user', views.)

urlpatterns = [
    path('auth/register/', views.register_user, name='register'),
]