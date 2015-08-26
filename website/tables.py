import django_tables2 as tables
from website.models import Transaction

class TransactionTable(tables.Table):
    class Meta:
        model = Transaction
        fields = ('id', 'date', 'amount', 'category', 'building', 'tenancy', 'person', 'description')
        order_by = ('-date')
