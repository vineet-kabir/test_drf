# Generated by Django 2.1.4 on 2019-02-03 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidcapital', '0013_soa_ar_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='debtor_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
