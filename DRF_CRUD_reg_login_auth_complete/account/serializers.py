from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.serializers import *
from .models import *

# start ClientSerializer #
class ClientSerializer(ModelSerializer):

    class Meta:
        model = Client
        exclude = ('created_at','updated_at','is_deleted','deleted_at')
# end ClientSerializer #