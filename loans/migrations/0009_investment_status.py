# Generated by Django 5.1.1 on 2024-10-20 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0008_investment_net_return_loan_loan_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='status',
            field=models.CharField(default='Open', null=True),
        ),
    ]
