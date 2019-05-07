from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .serializers import *

router = routers.DefaultRouter()
router.register(r'client', views.ClientViewSet) #For demo client

urlpatterns = [
    path('', include(router.urls)),

    # jwt endpoints
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('test/', views.TestView.as_view(), name='test'),
]