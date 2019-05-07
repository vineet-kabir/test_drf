from django.db import models
from django.db.models import Q
from rest_framework.response import Response

from django.utils import timezone


INVOICE_STATUS_CHOICES=(('pending','pending'),('reviewing','reviewing'),('approved','approved'))
TRANSACTION_TYPE_CHOICES=(('debit','debit'),('credit','credit'))
TERM_CHOICES=(('3', '3'),('6', '6'),('12', '12'))
SOA_STATUS_CHOICES=(('pending', 'pending'), ('submitted', 'submitted'), ('rejected', 'rejected'), ('draft', 'draft'), ('approved', 'approved'))

class TimeStamp(models.Model):
    """Base class containing all models common information."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted=models.BooleanField(default=False)
    deleted_at=models.DateTimeField(blank=True, null=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        """Define Model as abstract."""
        abstract = True

class Company(TimeStamp):
    name = models.CharField(max_length=255)
    
    def save(self, **kwargs):
        super(Company, self).save()
    
    class Meta:
        db_table = 'company'

class Client(TimeStamp):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ref_client_key = models.PositiveIntegerField(null=True)
    ref_client_no = models.CharField(max_length=255,null=True)
    ref_account_exec = models.CharField(max_length=255,null=True)

    def save(self, **kwargs):
        super(Client, self).save()
        self.company.save()
    
    class Meta:
        db_table = 'client'

class ClientFund(TimeStamp):
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    ar_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    funding_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    reserve_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    credit_commitee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    purchage_sales_agreement = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    discount_fees_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    credit_insurance_total_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    reserves_withheld_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    def save(self, **kwargs):
        super(ClientFund, self).save()
        self.client.save()
    
    class Meta:
        db_table = 'client_fund'

class ClientAccount(TimeStamp):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=64, unique=True)
    account_title =  models.CharField(max_length=64, null=True)
    transit_number =  models.PositiveIntegerField(null=True)
    institution_number =  models.PositiveIntegerField(null=True)
    bank_name =  models.CharField(max_length=64, null=True)
    # payment_method = models.CharField(max_length=64, null=True)
    # wire_fee_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    def save(self, **kwargs):
        super(ClientAccount, self).save()
        self.client.save()
    
    class Meta:
        db_table = 'client_account'

class Debtor(TimeStamp):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    ref_debtor_key = models.CharField(max_length=255,null=True)
    ref_debtor_no = models.CharField(max_length=255,null=True)
    ref_credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, **kwargs):
        super(Debtor, self).save()
        self.client.save()
    
    class Meta:
        db_table = 'debtor'
  
class SOA(TimeStamp):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=SOA_STATUS_CHOICES, default=SOA_STATUS_CHOICES[0][0])
    uploaded_supporting_docs = models.BooleanField(default=False)
    verification_calls = models.BooleanField(default=False)
    verification_call_notes = models.BooleanField(default=False)
    debtor_approval_emails = models.BooleanField(default=False)
    estoppel_letters = models.BooleanField(default=False)
    email_verification = models.BooleanField(default=False)
    is_priority = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    invoice_total = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    discount_fees = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    credit_insurance_total = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    reserves_withheld = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    additional_cash_reserve_held = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    miscellaneous_adjustment = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    reason_miscellaneous_adj = models.TextField(max_length=255, default='', blank=True)
    fee_adjustment = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    reason_fee_adj = models.CharField(max_length=255, default='', blank=True)
    additional_cash_reserve_release = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    high_priority = models.BooleanField(default=False)
    ar_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)


    def save(self, **kwargs):
        super(SOA, self).save()
        self.client.save()
    
    class Meta:
        db_table = 'soa'

class SOASupportingDocument(TimeStamp):
    soa = models.ForeignKey(SOA, on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    notes = models.TextField(null=True)
    name = models.CharField(max_length=255, null=True)
    
    def save(self, **kwargs):
        super(SOASupportingDocument, self).save()
        self.soa.save()
    
    class Meta:
        db_table = 'soa_supporting_document'

class SOADisbursement(TimeStamp):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)    
    soa = models.ForeignKey(SOA, on_delete=models.CASCADE, null=True)
    client_account_id= models.CharField(max_length=64, null=True, default='', blank=True)
    payee_account_id= models.CharField(max_length=64, null=True, default='', blank=True)
    payment_method = models.CharField(max_length=64, null=True)
    wire_fee_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)    
    tp_payment_fee_rate = models.CharField(max_length=64, null=True, blank=True)
    tp_ticket_number = models.CharField(max_length=64, null=True, blank=True)

    def save(self, **kwargs):
        super(SOADisbursement, self).save()
        self.client.save()
    
    class Meta:
        db_table = 'soa_disbursement'


class Invoice(TimeStamp):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    soa = models.ForeignKey(SOA, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=64, unique=True)
    invoice_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    po_number = models.CharField(max_length=64, blank=True)
    notes = models.TextField(default='', blank=True)
    added_by = models.CharField(max_length=255)
    verified_by = models.CharField(max_length=255)
    status = models.CharField(max_length=9, choices=INVOICE_STATUS_CHOICES, default=INVOICE_STATUS_CHOICES[0][0])
    terms = models.CharField(max_length=9, choices=TERM_CHOICES, default=TERM_CHOICES[0][0])
    is_credit_insured = models.BooleanField(default=False)
    debtor_name = models.CharField(max_length=255, null=True)

    def save(self, **kwargs):
        super(Invoice, self).save()
        self.client.save()
        self.soa.save()
    
    class Meta:
        db_table = 'invoice'

class Payee(TimeStamp):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    def save(self, **kwargs):
        super(Payee, self).save()
        self.client.save()
    
    class Meta:
        db_table = 'payee'

class PayeeAccount(TimeStamp):
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=255, unique=True)
    account_title =  models.CharField(max_length=255, null=True)
    transit_number =  models.PositiveIntegerField(null=True)
    institution_number =  models.PositiveIntegerField(null=True)
    bank_name =  models.CharField(max_length=255, null=True)
    bank_account =  models.CharField(max_length=255, null=True)

    def save(self, **kwargs):
        super(PayeeAccount, self).save()
        self.payee.save()
    
    class Meta:
        db_table = 'payee_account'


class PayeeSupportingDocument(TimeStamp):
    soa = models.ForeignKey(SOA, on_delete=models.CASCADE, null=True)
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    notes = models.TextField(null=True)
    name = models.CharField(max_length=255, null=True)
    
    def save(self, **kwargs):
        super(PayeeSupportingDocument, self).save()
        self.payee.save()
        self.soa.save()
    
    class Meta:
        db_table = 'payee_supporting_document'
