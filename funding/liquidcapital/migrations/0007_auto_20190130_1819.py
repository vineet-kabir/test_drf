# Generated by Django 2.1.4 on 2019-01-30 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidcapital', '0006_soa_high_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soa',
            name='reason_fee_adj',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='soa',
            name='reason_miscellaneous_adj',
            field=models.TextField(blank=True, default='', max_length=255),
        ),
    ]
