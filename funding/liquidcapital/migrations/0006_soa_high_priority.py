# Generated by Django 2.1.4 on 2019-01-30 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liquidcapital', '0005_auto_20190130_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='soa',
            name='high_priority',
            field=models.BooleanField(default=False),
        ),
    ]
