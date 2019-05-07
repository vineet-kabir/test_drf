from django.urls import path, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'company', views.CompanyViewSet)
router.register(r'client', views.ClientViewSet)
router.register(r'client-fund', views.ClientFundViewSet)
router.register(r'client-account', views.ClientAccountViewSet)
router.register(r'debtor', views.DebtorViewSet)
router.register(r'soa', views.SOAViewSet)
router.register(r'soa-supporting-document', views.SOASupportingDocumentViewSet)
router.register(r'soa-disbursement', views.SOADisbursementViewSet)
router.register(r'invoice', views.InvoiceViewSet)
router.register(r'payee', views.PayeeViewSet)
router.register(r'payee-account', views.PayeeAccountViewSet)
router.register(r'payee-supporting-document', views.PayeeSupportingDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('new-invoice-schedule/', views.new_invoice_schedule),
    path('new-invoice/', views.new_invoice),
    path('view-client-details/', views.view_client_details),
    path('complete-invoice/', views.complete_invoice),
    path('get_payee_account/', views.get_payee_account),
    path('get_SOADisbursement_by_SOA/', views.get_SOADisbursement_by_SOA),
    path('get_debtor_by_client/', views.get_debtor_by_client),
    path('get_payee_by_client/', views.get_payee_by_client),
    path('get_payee_account_by_payee/', views.get_payee_account_by_payee),
    # path('additional-payee-details/', views.additional_payee_details),
    
    # Resources integration
    path('presigned_url/', views.get_presigned_url),
    path('save_file/', views.save_file),
]
