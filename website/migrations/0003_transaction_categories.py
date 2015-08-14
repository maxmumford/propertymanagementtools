# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from website.models import TransactionCategory

def add_transaction_categories(*args, **kwargs):
    # create transaction categories
    categories = [
        {'name': 'Rent', 'hmrc_code': '20', 'description': 'Total rents and other income from property'},
        {'name': 'Rates & Insurance', 'hmrc_code': '24', 'description': 'Rent, rates, insurance, ground rents etc.'},
        {'name': 'Maintenance', 'hmrc_code': '25', 'description': 'Property repairs and maintenance'},
        {'name': 'Financing', 'hmrc_code': '26', 'description': 'Loan interest and other financial costs (e.g. mortgage repayments)'},
        {'name': 'Legal & Professional', 'hmrc_code': '27', 'description': 'Legal, management and other professional fees'},
        {'name': 'Services', 'hmrc_code': '28', 'description': 'Costs of services provided, including wages (e.g. gas and electricity)'},
        {'name': 'Other', 'hmrc_code': '29', 'description': 'Other allowable property expenses'},
    ]
    for category in categories:
        category_record, created = TransactionCategory.objects.get_or_create(**category)

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_groups'),
    ]

    operations = [
        migrations.RunPython(add_transaction_categories),
    ]
