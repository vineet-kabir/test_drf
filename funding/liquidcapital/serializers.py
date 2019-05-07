from rest_framework.serializers import ModelSerializer

from .models import *

class CompanySerializer(ModelSerializer):

    class Meta:
        model = Company
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class ClientSerializer(ModelSerializer):

    class Meta:
        model = Client
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class ClientFundSerializer(ModelSerializer):

    class Meta:
        model = ClientFund
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class ClientAccountSerializer(ModelSerializer):

    class Meta:
        model = ClientAccount
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class DebtorSerializer(ModelSerializer):

    class Meta:
        model = Debtor
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class SOASerializer(ModelSerializer):

    class Meta:
        model = SOA
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class SOADisbursementSerializer(ModelSerializer):

    class Meta:
        model = SOADisbursement
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class SOASupportingDocumentSerializer(ModelSerializer):

    class Meta:
        model = SOASupportingDocument
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class InvoiceSerializer(ModelSerializer):

    class Meta:
        model = Invoice
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class PayeeSerializer(ModelSerializer):

    class Meta:
        model = Payee
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class PayeeAccountSerializer(ModelSerializer):

    class Meta:
        model = PayeeAccount
        exclude = ('created_at','updated_at','is_deleted','deleted_at')

class PayeeSupportingDocumentSerializer(ModelSerializer):

    class Meta:
        model = PayeeSupportingDocument
        exclude = ('created_at','updated_at','is_deleted','deleted_at')
