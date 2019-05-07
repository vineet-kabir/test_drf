from django.contrib import admin
from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path('', get_swagger_view(title='LC-Funding API')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('liquidcapital.urls')),
]
