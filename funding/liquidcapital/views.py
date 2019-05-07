from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django_filters import rest_framework as filters

from .serializers import *
from .models import *

from datetime import timedelta
from django.http import JsonResponse

import requests

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

class CompanyViewSet(SoftDelete):
       
    queryset = Company.objects.filter(is_deleted=False)
    serializer_class = CompanySerializer

class ClientViewSet(SoftDelete):
       
    queryset = Client.objects.filter(is_deleted=False)
    serializer_class = ClientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('company', 'name', )

class ClientFundViewSet(SoftDelete):
       
    queryset = ClientFund.objects.filter(is_deleted=False)
    serializer_class = ClientFundSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('client', )

class ClientAccountViewSet(SoftDelete):
       
    queryset = ClientAccount.objects.filter(is_deleted=False)
    serializer_class = ClientAccountSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('client', 'account_number', )

class DebtorViewSet(SoftDelete):
       
    queryset = Debtor.objects.filter(is_deleted=False)
    serializer_class = DebtorSerializer

class SOASupportingDocumentViewSet(SoftDelete):
       
    queryset = SOASupportingDocument.objects.filter(is_deleted=False)
    serializer_class = SOASupportingDocumentSerializer

class SOADisbursementViewSet(SoftDelete):
       
    queryset = SOADisbursement.objects.filter(is_deleted=False)
    serializer_class = SOADisbursementSerializer

class SOAViewSet(SoftDelete):
       
    queryset = SOA.objects.filter(is_deleted=False)
    serializer_class = SOASerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('client', 
                        'status', 
                        'uploaded_supporting_docs',
                        'verification_calls',
                        'verification_call_notes',
                        'debtor_approval_emails',
                        'estoppel_letters',
                        'email_verification',
                        'is_priority',
                        'notes',
                        'invoice_total',
                        'discount_fees',
                        'credit_insurance_total',
                        'reserves_withheld',
                        'additional_cash_reserve_held',
                        'miscellaneous_adjustment',
                        'reason_miscellaneous_adj',
                        'fee_adjustment',
                        'additional_cash_reserve_release',
                        'advance_amount',
                        'high_priority',
                        'ar_balance',
                        
    )


class InvoiceViewSet(SoftDelete):
       
    queryset = Invoice.objects.filter(is_deleted=False)
    serializer_class = InvoiceSerializer

class PayeeViewSet(SoftDelete):
       
    queryset = Payee.objects.filter(is_deleted=False)
    serializer_class = PayeeSerializer

class PayeeAccountViewSet(SoftDelete):
       
    queryset = PayeeAccount.objects.filter(is_deleted=False)
    serializer_class = PayeeAccountSerializer

class PayeeSupportingDocumentViewSet(SoftDelete):
       
    queryset = PayeeSupportingDocument.objects.filter(is_deleted=False)
    serializer_class = PayeeSupportingDocumentSerializer


@api_view(['POST'])
@permission_classes((AllowAny, ))
def new_invoice_schedule(request):
    output = {}
    company_id = request.data.get('company')
    clients = Client.objects.filter(Q(is_deleted=False) & Q(company__id=company_id))
    for client in clients:
        client_accounts = ClientAccount.objects.filter(Q(is_deleted=False) & Q(client=client))
        obj = ClientSerializer(client).data
        ca_s = ClientAccountSerializer(client_accounts, many=True).data
        obj.update({'account': ca_s})      
        output.update({'' + str(client.id): obj})
    
    return Response(output, status=200)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def view_client_details(request):
    try:
        output = {}
        client_id = request.data.get('client_id', None)
        client = Client.objects.filter(is_deleted=False).get(id=client_id)

        # 2. fund details
        client_fund = ClientFund.objects.filter(is_deleted=False).get(client=client)
        serializer = ClientFundSerializer(client_fund)
        output.update({'client_fund': serializer.data})
        
        # 3. debtors name list
        debtors = Debtor.objects.filter(Q(is_deleted=False) & Q(client=client))
        debtors_list = []
        if debtors:
            serializer = DebtorSerializer(debtors, many=True)
            debtors_list = serializer.data

        output.update({'debtors': debtors_list})

        # 3. bank account name list
        client_accounts = ClientAccount.objects.filter(Q(is_deleted=False) & Q(client=client))
        client_accounts_list = []
        if client_accounts:
            serializer = ClientAccountSerializer(client_accounts, many=True)
            client_accounts_list = serializer.data

        output.update({'client_accounts': client_accounts_list})
        
        return Response(output)
    except Client.DoesNotExist:
        return Response({'status':'error','message': 'client does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except ClientFund.DoesNotExist:
        return Response({'status':'error','message': 'client fund does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

    

@api_view(['POST'])
@permission_classes((AllowAny, ))
def new_invoice(request):
    try:
        request_obj = request.data
        buildSchedule = request_obj['buildSchedule']
        reviewConfirmation = request_obj['reviewConfirmation']
        disbursementDetails = request_obj['disbursementDetails']
        
        invoices = buildSchedule['invoices']
        
        # save invoices
        client = Client.objects.filter(Q(is_deleted=False)).get(id=invoices[0]['client'])

        start_date = timezone.now().date()
        end_date = start_date + timedelta( days=1 ) 
        
        soas = SOA.objects.filter(Q(is_deleted=False) & Q(created_at__range=(start_date, end_date)))
        
        if not soas:
            return Response({'status':'error','message': 'soa does not exist'}, status=status.HTTP_404_NOT_FOUND)
        soa = soas[0]
        
        # soa = SOA.objects.filter(Q(is_deleted=False)).get(id=invoices[0]['soa'])
        for invoice in invoices:
            invoice_obj = {
                "client": client,
                "soa": soa,
                "invoice_number": invoice.get('invoiceNumber'),
                "invoice_date": invoice.get('invoiceDate'),
                "amount": invoice.get('amount'),
                # "discount_fees": invoice.get('discountFees'),
                "po_number": invoice.get('poNumber'),
                "notes": invoice.get('notes'),
                "added_by": invoice.get('addedBy'),
                "verified_by": invoice.get('verifiedBy'),
                "status": invoice.get('status'),
                "terms": invoice.get('terms'),
                "is_credit_insured": invoice.get('creditInsured'),
                "debtor_name": invoice.get('debtorName')
            }
            inv = Invoice.objects.create(**invoice_obj)
            inv.save()

        # save soa details
        soa.uploaded_supporting_docs = reviewConfirmation.get('uploadedInvoices', False)
        soa.verification_calls = reviewConfirmation.get('verificationCall', False)
        soa.debtor_approval_emails = reviewConfirmation.get('approvalEmails', False)
        soa.estoppel_letters = reviewConfirmation.get('estoppelLetters', False)
        soa.email_verification = reviewConfirmation.get('emailVerifications', False)
        soa.is_priority = disbursementDetails.get('highPriority', False)
        soa.notes = reviewConfirmation.get('verificationComments', '')
        soa.save()


        return Response(request.data, status=201)
    
    except Client.DoesNotExist:
        return Response({'status':'error','message': 'client does not exist'}, status=status.HTTP_404_NOT_FOUND)
    # except SOA.DoesNotExist:
    #     return Response({'status':'error','message': 'soa does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

@api_view(['POST'])
@permission_classes((AllowAny, ))
def complete_invoice(request):
    try:
        request_obj = request.data
        buildSchedule = request_obj['buildSchedule']        
        invoices = buildSchedule['invoices']
        attachments = buildSchedule['attachments']
        client_id = buildSchedule['client_id']
        soa_id = buildSchedule['soa_id']

        # save invoices
        client = Client.objects.filter(pk=client_id).get()
        if not client:
            return Response({'status':'error','message': 'client does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # print(client)
        get_soa = SOA.objects.filter(pk=soa_id).get()

        if not get_soa:
            return Response({'status':'error','message': 'soa does not exist'}, status=status.HTTP_404_NOT_FOUND)

        for invoice_obj in invoices:
            add_defaults = {
                "invoice_date": invoice_obj.get('invoice_date'),
                "amount": invoice_obj.get('amount'),
                "po_number": invoice_obj.get('po_number'),
                "added_by": invoice_obj.get('added_by'),
                "verified_by": invoice_obj.get('verified_by'),
                "terms": invoice_obj.get('terms'),
                "is_credit_insured": invoice_obj.get('is_credit_insured'),
                "debtor_name": invoice_obj.get('debtor_name'),
                "soa": get_soa,
                "client": client,
            }

            Invoice.objects.update_or_create(**{
                'invoice_number' : invoice_obj.get('invoice_number')
                }, defaults=add_defaults)

        for attach_files in attachments:
            SOASupportingDocument.objects.update_or_create(**{
                'soa':get_soa,
                'url':attach_files['url'],
                'name':attach_files['name'],
            })

        return Response(request.data, status=201)
    
    except Client.DoesNotExist:
        return Response({'status':'error','message': 'client does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_payee_account(request):
    try:
        if request.method == 'POST':
            payee_id = request.POST.get('payee_id', None)
            payee = PayeeAccount.objects.values('payee', 'account_number', 'account_title', 'transit_number', 'institution_number', 'bank_name', 'bank_account').filter(Q(is_deleted=False) & Q(payee=payee_id)) 
            if payee:
                acc_obj = {}
                acc_obj.update({'payee': payee})
                return Response(acc_obj)
            else:
                return Response({'status':'error','message': 'Payee Account does not exist'})
        else:
            return Response({'status':'error','message': 'Invalid Request'}, status=status.HTTP_403_FORBIDDEN)
         
    except Client.DoesNotExist:
        return Response({'status':'error','message': 'Payee Account does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PayeeAccount.DoesNotExist:
        return Response({'status':'error','message': 'The account doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_SOADisbursement_by_SOA(request):
    try:
        if request.method == 'POST':
            soa_id = request.data.get('soa_id', None)
            invoice_status = request.data.get('invoice_status', None)
            output = {}
            soa_list = []
            if soa_id:
                soa = SOA.objects.filter(Q(is_deleted=False) & Q(id=soa_id)).order_by('-created_at')
                if not soa.exists():
                    return Response({'status':'error','message': 'SOA not found'}, status=404)
            else:  
                soa = SOA.objects.filter(is_deleted=False).order_by('-created_at')
            
            # Filter To Get Different Type Of List in SOA
            if invoice_status == '' or not invoice_status:
                update_soa = soa
            elif invoice_status == 'pending':
                update_soa = soa.filter(status='pending')
            
            elif invoice_status == 'submitted':
                update_soa = soa.filter(status='submitted')
            
            elif invoice_status == 'rejected':
                update_soa = soa.filter(status='rejected')
            
            elif invoice_status == 'draft':
                update_soa = soa.filter(status='draft')

            elif invoice_status == 'approved':
                update_soa = soa.filter(status='approved')
            for ss in update_soa:
                acc_obj = {
                'id': ss.id, 
                'client': ss.client_id,
                'status': ss.status,
                'uploaded_supporting_docs': ss.uploaded_supporting_docs,
                'verification_calls': ss.verification_calls, 
                'verification_call_notes': ss.verification_call_notes,
                'debtor_approval_emails': ss.debtor_approval_emails,
                'estoppel_letters': ss.estoppel_letters,
                'email_verification': ss.email_verification, 
                'is_priority': ss.is_priority,
                'notes': ss.notes,
                'invoice_total': ss.invoice_total,
                'discount_fees': ss.discount_fees, 
                'credit_insurance_total': ss.credit_insurance_total,
                'reserves_withheld': ss.reserves_withheld,
                'additional_cash_reserve_held': ss.additional_cash_reserve_held,  
                'miscellaneous_adjustment': ss.miscellaneous_adjustment,
                'reason_miscellaneous_adj': ss.reason_miscellaneous_adj,  
                'fee_adjustment': ss.fee_adjustment,
                'reason_fee_adj': ss.reason_fee_adj,        
                'additional_cash_reserve_release': ss.additional_cash_reserve_release,        
                'advance_amount': ss.advance_amount,               
                'high_priority': ss.high_priority,        
                'ar_balance': ss.ar_balance,
                'updated_at': ss.updated_at,
                'attachments' : []           
                }
                ref_client_details = Client.objects.values('name', 'ref_client_no').filter(Q(is_deleted=False) & Q(id=ss.client_id))
                acc_obj.update({'ref_client_details': ref_client_details})
                
                client_account_details = ClientAccount.objects.values('account_number', 'bank_name').filter(Q(is_deleted=False) & Q(client=ss.client_id))
                acc_obj.update({'client_account_details': client_account_details})

                soa_disbursement = SOADisbursement.objects.values('id', 'client', 'soa', 'client_account_id', 'payee_account_id', 'payment_method', 'wire_fee_rate', 'amount', 'tp_payment_fee_rate', 'tp_ticket_number', 'updated_at').filter(Q(is_deleted=False) & Q(soa=ss.id))
                acc_obj.update({'soa_disbursement': soa_disbursement})
                
                soa_supporting_docs = SOASupportingDocument.objects.values('url', 'notes', 'name').filter(Q(is_deleted=False) & Q(soa=ss.id))
                acc_obj.update({'attachments': soa_supporting_docs})
                     
                invoice = Invoice.objects.values('id', 'client', 'soa' ,'invoice_number', 'invoice_date', 'amount', 'po_number', 'notes', 'added_by', 'verified_by', 'status', 'terms', 'is_credit_insured', 'debtor_name', 'updated_at').filter(Q(is_deleted=False) & Q(soa=ss.id))
                acc_obj.update({'invoice': invoice})
                
                client_account = ClientAccount.objects.values('id', 'client', 'account_number' ,'account_title', 'transit_number', 'institution_number', 'bank_name', 'updated_at').filter(Q(is_deleted=False) & Q(client=ss.client_id))
                acc_obj.update({'client_account': client_account})
               
                payee = Payee.objects.values('id').filter(Q(is_deleted=False) & Q(client=ss.client_id))
                for pay in payee:
                    payee_account = PayeeAccount.objects.values('id', 'payee', 'account_number', 'account_title', 'transit_number', 'institution_number', 'bank_name', 'bank_account', 'updated_at').filter(Q(is_deleted=False) & Q(payee=pay['id']))
                    acc_obj.update({'payee_account': payee_account})
                soa_list.append(acc_obj)
                   
            output.update({'soa': soa_list})
            return Response(output)
        else:
            return Response({'status':'error','message': 'Invalid Request'}, status=status.HTTP_403_FORBIDDEN)
    
    except KeyError as e:
        print(str(e))
        return Response({'status':'error','message': 'KeyError:' + str(e) + ' missing'}, status=status.HTTP_403_FORBIDDEN)
    except SOA.DoesNotExist:
        return Response({'status':'error','message': 'SOA does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_debtor_by_client(request):
    try:
        if request.method == 'POST':
            client_id = request.POST.get('client_id', None)
            debtor = Debtor.objects.values('id', 'client', 'name', 'ref_debtor_key', 'ref_debtor_no', 'ref_credit_limit').filter(Q(is_deleted=False) & Q(client=client_id))
            if debtor:
                acc_obj = {}
                acc_obj.update({'debtor': debtor})
                return Response(acc_obj)
            else:
                return Response({'status':'error','message': 'Debtor does not exist'})
        else:
            return Response({'status':'error','message': 'Invalid Request'}, status=status.HTTP_403_FORBIDDEN)
    
    except KeyError as e:
        print(str(e))
        return Response({'status':'error','message': 'KeyError:' + str(e) + ' missing'}, status=status.HTTP_403_FORBIDDEN)
    except Debtor.DoesNotExist:
        return Response({'status':'error','message': 'Debtor does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_payee_by_client(request):
    try:
        if request.method == 'POST':
            client_id = request.POST.get('client_id', None)
            payee = Payee.objects.values('id', 'client', 'name').filter(Q(is_deleted=False) & Q(client=client_id))
            if payee:
                acc_obj = {}
                acc_obj.update({'payee': payee})
                return Response(acc_obj)
            else:
                return Response({'status':'error','message': 'payee does not exist'})
        else:
            return Response({'status':'error','message': 'Invalid Request'}, status=status.HTTP_403_FORBIDDEN)
    
    except KeyError as e:
        print(str(e))
        return Response({'status':'error','message': 'KeyError:' + str(e) + ' missing'}, status=status.HTTP_403_FORBIDDEN)
    except Payee.DoesNotExist:
        return Response({'status':'error','message': 'Payee does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 

@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_payee_account_by_payee(request):
    try:
        if request.method == 'POST':
            payee_id = request.POST.get('payee_id', None)
            payee_account = PayeeAccount.objects.values('id', 'payee', 'account_number', 'account_title', 'transit_number', 'institution_number', 'bank_name', 'bank_account').filter(Q(is_deleted=False) & Q(payee=payee_id))
            if payee_account:
                acc_obj = {}
                acc_obj.update({'payee_account': payee_account})
                
                return Response(acc_obj)
            else:
                return Response({'status':'error','message': 'Payee Account does not exist'})
        else:
            return Response({'status':'error','message': 'Invalid Request'}, status=status.HTTP_403_FORBIDDEN)
    
    except KeyError as e:
        print(str(e))
        return Response({'status':'error','message': 'KeyError:' + str(e) + ' missing'}, status=status.HTTP_403_FORBIDDEN)
    except PayeeAccount.DoesNotExist:
        return Response({'status':'error','message': 'Payee Account does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response({'status': 'error', 'message': str(e)}, status=500) 


@api_view(['PUT'])
@permission_classes((AllowAny, ))
def get_presigned_url(request):
    # TODO: Need to move to env file
    url = 'http://127.0.0.1:8000'
    business_id = 10 # Liquid Capital
    folder_id = 438 # Root Folder
    
    try:
        request_obj = request.data
        content_type = request_obj['content_type']

        get_request = requests.put(url + '/resources/pre_signed_url/', data = {
            'business_id': business_id,
            'folder_id': folder_id,
            'content_type': content_type,
            })

        return Response(get_request.json())
        # get_request.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(str(e))
        return Response({
            'status':'error',
            'message': 'Exception:' + str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(str(e))
        return Response({
            'status':'error',
            'message': 'Exception:' + str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def save_file(request):
    # TODO: Need to move to env file
    url = 'http://127.0.0.1:8000'
    business_id = 10 # Liquid Capital
    folder_id = 438 # Root Folder
    
    try:
        request_obj = request.data
        file_path = request_obj['file_path']        
        
        get_request = requests.post(url + '/resources/save_file/', data = {
            'business_id': business_id,
            'folder_id': folder_id,
            'file_path': file_path,
            })

        return Response(get_request.json())
        # get_request.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(str(e))
        return Response({
            'status':'error',
            'message': 'Exception:' + str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(str(e))
        return Response({
            'status':'error',
            'message': 'Exception:' + str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
