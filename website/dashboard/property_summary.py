from decimal import *

# set decimal arithmatic context
context = getcontext()
context.rounding=ROUND_HALF_UP

class PropertySummary():

    def __init__(self, prop, transactions):
        self.prop = prop
        self.transactions = transactions

        self._total_income = Decimal()
        self._total_expense = Decimal()

    @property
    def balance(self):
        return (self._total_income - self._total_expense).quantize(Decimal('1.00'))

    @property
    def total_income(self):
        return self._total_income.quantize(Decimal('1.00'))

    @property
    def total_expense(self):
        return self._total_expense.quantize(Decimal('1.00'))

    def __str__(self):
        return self.prop.name + ": Total income is %(income)s with %(expense)s in expenses, leaving a balance of %(balance)s." % \
                        {'income': self.total_income, 'expense': self.total_expense, 'balance': self.balance}

    def calculate(self):
        self._calculate_total_income()
        self._calculate_total_expense()

    def _calculate_total_income(self):
        self._total_income += Decimal(str(sum([transaction.amount for transaction in self.transactions if transaction.category.hmrc_code == '20'])))

    def _calculate_total_expense(self):
        self._total_expense += Decimal(str(sum([transaction.amount for transaction in self.transactions if transaction.category.hmrc_code != '20'])))
