# Generated by Django 2.1.4 on 2019-01-31 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidcapital', '0009_auto_20190131_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soadisbursement',
            name='tp_payment_fee_rate',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='soadisbursement',
            name='tp_ticket_number',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
