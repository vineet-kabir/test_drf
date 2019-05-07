from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import *
from rest_framework.status import *
from rest_framework import viewsets
from rest_framework import status
from django_filters import rest_framework as filters

from .serializers import *
from django.contrib.auth import get_user_model
from rest_framework.generics import *

#start SoftDelete #
class SoftDelete(viewsets.ModelViewSet):

    def destroy(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        return Response({
            'status':'success', 
            'message': 'Delete Success'
            }, 
            status = status.HTTP_200_OK
        ) 
    class Meta:
        abstract = True
#end SoftDelete #

#start ClientViewSet #
class ClientViewSet(SoftDelete):       
    queryset = Client.objects.filter(is_deleted=False)
    serializer_class = ClientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('name', 'mobile',)
#end ClientViewSet #

# start TestView for JWT Token #
class TestView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
# end TestView for JWT Token #