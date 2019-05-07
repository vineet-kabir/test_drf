from django.core.management.base import BaseCommand
from django.utils import timezone

import requests

from liquidcapital.models import Company, Client, ClientAccount, ClientFund, Debtor

class Command(BaseCommand):
    help = 'Sync Third Party Database'

    def handle(self, *args, **kwargs):
        # Third 
        url = 'https://lc-third-party.dev.api.50c.io'
        app_id = 'ATnfvRJAXe0xpHTfFy1yP3gPaD2uBQc1'
        app_secret = 'RLtCnIdpX6bRietkhkQmsxqwGnYrMG2r'

        all_client = requests.get(url + '/api/v1/cadence/clients/discountsReserves', headers={'app-id':app_id, 'app-secret': app_secret})
        all_client = all_client.json()

        company = Company.objects.filter(pk=1).get()

        for client in all_client:
            Client.objects.update_or_create(
                    ref_client_key=client['ClientKey'],
                    ref_client_no=client['ClientNo'],                
                    defaults={"company":company, "name": client['Name'], "ref_account_exec":client['AcctExec']},
                )

            # Need to fix this stupid shit
            g_client = Client.objects.get(ref_client_key=client['ClientKey'])
            # # print(g_client.id)
            ClientFund.objects.update_or_create(
                client=g_client,
                defaults={'reserves_withheld_percentage':client['RsvEscrowRate'],
                'discount_fees_percentage':client['FeeEscrowRate']}
            )

            # Pulling Debtors
            all_debtors = requests.get(url + '/api/v1/cadence/clients/debtors?clientKey=' + str(client['ClientKey']), headers={'app-id':app_id, 'app-secret': app_secret})
            all_debtors = all_debtors.json()
            for g_debtor in all_debtors:
                if 'DebtorKey' in g_debtor:
                    debtor_details = requests.get(url + '/api/v1/cadence/debtors?debtorKey=' + str(g_debtor['DebtorKey']), headers={'app-id':app_id, 'app-secret': app_secret})
                    debtor_details = debtor_details.json()
                    for d_details in debtor_details:
                        Debtor.objects.update_or_create(
                            client=g_client,
                            ref_debtor_key=d_details['DebtorKey'],
                            defaults={
                                'ref_debtor_no':d_details['DebtorNo'],
                                'ref_credit_limit':d_details['TotalCreditLimit'],
                                'name':d_details['Name']
                            }
                        )
            print({
                'client' : client,
                'debtors' : all_debtors
            })