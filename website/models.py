import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import *

from django.conf import settings

# set decimal arithmatic context
context = getcontext()
context.rounding=ROUND_HALF_UP

from django.db import models
from django.contrib.auth.models import User
from fields import DatePickerField

from invoice import Invoice

TITLE_CHOICES = (
    ('MR', 'Mr.'),
    ('MRS', 'Mrs.'),
    ('MS', 'Ms.'),
)

def currency(view_function):
    def _wrapped_currency(request, *args, **kwargs): 
        return round(view_function(request, *args, **kwargs), 2)
    return _wrapped_currency

class Building(models.Model):
    owner = models.ForeignKey(User, blank=False)
    name = models.CharField(max_length=35, blank=False)
    address_line_1 = models.CharField(max_length=45)
    address_line_2 = models.CharField(max_length=45)
    city = models.CharField(max_length=35)
    county = models.CharField(max_length=35)
    postcode = models.CharField(max_length=35)
    country = models.CharField(max_length=35)
    purchase_date = DatePickerField()

    def __str__(self):
        return self.name

    @property
    def rooms_count(self):
        return self.room_set.count()

    @property
    def rooms_full_count(self):
        return len([tenancy for tenancy in self.tenancy_set.all() if tenancy.active == True])

    @property
    @currency
    def tenancy_balance(self):
        return sum([tenancy.balance for tenancy in self.tenancy_set.all() if tenancy.active == True])

    @property
    @currency
    def profit_per_day(self):
        now = datetime.now().date()
        days_passed = (now - self.purchase_date).days
        return self._total_income / days_passed

    @property
    @currency
    def profit_per_month(self):
        return self.profit_per_day * 31

    @property
    @currency
    def profit_per_year(self):
        return self.profit_per_day * 365

    @property
    def notices(self):
        return self._notices

    @property
    @currency
    def balance(self):
        return (self._total_income - self._total_expense).quantize(Decimal('1.00'))

    @property
    @currency
    def total_income(self):
        return self._total_income.quantize(Decimal('1.00'))

    @property
    @currency
    def total_expense(self):
        return self._total_expense.quantize(Decimal('1.00'))

    def __str__(self):
        return self.name

    def calculate(self):
        self._total_income = Decimal()
        self._total_expense = Decimal()
        self._notices = []

        self._calculate_total_income()
        self._calculate_total_expense()
        self._create_notices()

    def _calculate_total_income(self):
        self._total_income += Decimal(str(sum([transaction.amount for transaction in self.transaction_set.all() if transaction.category.hmrc_code == '20'])))

    def _calculate_total_expense(self):
        self._total_expense += Decimal(str(sum([transaction.amount for transaction in self.transaction_set.all() if transaction.category.hmrc_code != '20'])))

    def _create_notices(self):
        for tenancy in self.tenancy_set.all():
            two_months_from_now = datetime.now().date() + relativedelta(months=2)
            if tenancy.active and tenancy.end_date < two_months_from_now:
                self._notices.append('Tenancy ending within 2 months')

class Room(models.Model):
    owner = models.ForeignKey(User, blank=False)
    name = models.CharField(max_length=35, blank=False)
    building = models.ForeignKey(Building, blank=False)

    def __str__(self):
        return self.name

class Person(models.Model):
    owner = models.ForeignKey(User, blank=False)
    title = models.CharField(max_length=35, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=35, blank=False)
    last_name = models.CharField(max_length=35, blank=False)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=25)

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.name

class Tenancy(models.Model):
    # Django field definitions
    owner = models.ForeignKey(User, blank=False)
    start_date = DatePickerField(blank=False)
    end_date = DatePickerField(blank=False)
    building = models.ForeignKey(Building, blank=False)
    rooms = models.ManyToManyField(Room, blank=False)
    people = models.ManyToManyField(Person, blank=False)

    # tenancy summation properties
    @property
    def active(self):
        now = datetime.now().date()
        return self.start_date < now and self.end_date > now

    @property
    def balance(self):
        return (self.total_paid - self.total_charged + sum(self._surplus.values())).quantize(Decimal('1.00'))

    @property
    def total_charged(self):
        return Decimal(str(sum([invoice.amount_due for invoice in self._invoices]))).quantize(Decimal('1.00'))

    @property
    def total_paid(self):
        return Decimal(str(sum([invoice.amount_paid for invoice in self._invoices]))).quantize(Decimal('1.00'))

    @property
    def surplus(self):
        return sum([surplus.value() for surplus in self._surplus]).quantize(Decimal('1.00'))

    @property
    def rent_payments(self):
        return self.transaction_set.filter(category__hmrc_code='20')

    def __str__(self):
        return '%(people)s in %(building)s from %(from)s to %(to)s' % \
                    {'people': ', '.join([person.first_name for person in self.people.all()]), 'building': self.building.name, \
                    'from': datetime.strftime(self.start_date, settings.FRIENDLY_DATE), 'to': datetime.strftime(self.end_date, settings.FRIENDLY_DATE)}

    @property
    def invoices(self):
        return self._invoices

    # tenancy summation calculation
    def calculate(self):
        self._invoices = []
        self.date = self.start_date
        self._surplus = {}

        self._generate_invoices()
        self._allocate_invoice_payments()

    def _generate_invoices(self):
        # go from month to month creating invoices
        while not self._all_months_processed():
            # calculate amount payable and invoice end date
            invoice_end_date = date(self.date.year, self.date.month, self._get_days_in_month(self.date))
            amount_due = Decimal()
            chargable_days_for_month = self._get_chargable_days_for_month(self.date, self.end_date)
            for day in range(1, chargable_days_for_month + 1):
                daily_rent = self._get_rent_for_day(self.date.replace(day=day))
                amount_due = amount_due + daily_rent

            # create invoice and save it, then advance to the next month
            self._invoices.append(Invoice(self.date, invoice_end_date, amount_due))
            self._next_month()

    def _allocate_invoice_payments(self):
        """ 
        Allocate transactions to invoices.
        For each invoice, find payments for that particular period and allocate them.
        Record surpluses and allocate them to oldest unpaid invoices first.
        """
        # allocate normal payments
        for invoice in self._invoices:
            transactions = self.rent_payments.filter(date__gte=invoice.date, date__lte=invoice.end_date).all()
            for transaction in transactions:
                payment_amount = Decimal(str(transaction.amount))
                if payment_amount > invoice.deficit:
                    payment_amount = invoice.deficit
                    self._surplus[transaction] = Decimal(str(transaction.amount)) - payment_amount
                invoice.make_payment(transaction, payment_amount)

        # allocate surplus payments
        for invoice in self._invoices:
            if invoice.in_deficit:
                new_surplus_list = {}
                for transaction, surplus in self._surplus.iteritems():
                    if invoice.in_deficit:
                        payment_amount = surplus
                        if payment_amount > invoice.deficit:
                            payment_amount = invoice.deficit
                            surplus = surplus - payment_amount
                        else:
                            surplus = Decimal('0')
                        invoice.make_payment(transaction, payment_amount)
                    if surplus > Decimal('0'):
                        new_surplus_list[transaction] = surplus
                self._surplus = new_surplus_list

    def _get_rent_for_day(self, date):
        # calculate the rent for the day of date based on rent_price records
        rent_for_day = None
        days_in_month = self._get_days_in_month(date)
        for rent_price in self.rentprice_set.all():
            if date >= rent_price.start_date and date <= rent_price.end_date:
                # day falls within this rent_price
                rent_for_day = Decimal(str(rent_price.price)) / Decimal(str(days_in_month))
                break
        if rent_for_day == None:
            raise InvalidDataError("Could not find a rent price for the date %s" % str(date))
        return rent_for_day

    def _get_chargable_days_for_month(self, date, end_date):
        # calculate the number of chargable days
        chargable_days = 0
        if date.year == self.end_date.year and date.month == self.end_date.month:
            # last month of the tenancy
            chargable_days = self.end_date.day - (date.day - 1)
        else:
            # either first month or middle month
            chargable_days = self._get_days_in_month(date) - (date.day - 1)
        return chargable_days

    def _get_days_in_month(self, date):
        # return number of days in the month
        return calendar.monthrange(date.year, date.month)[1]

    def _get_end_year_and_month(self):
        end_month = self.end_date.month
        end_year = self.end_date.year
        now = datetime.now()
        if now.date() < self.end_date:
            end_month = now.month
            end_year = now.year
        return (end_year, end_month)

    def _all_months_processed(self):
        # stop processing tenancy when self.date is in the same month as the tenancy end date, or now, whichever is sooner
        end_year, end_month = self._get_end_year_and_month()
        return (self.date.year <= end_year and self.date.month <= end_month) == False

    def _next_month(self):
        # increments self.date to be the first of the next month
        self.date = self.date + relativedelta(months=1)
        self.date = self.date.replace(day=1)

class RentPrice(models.Model):
    owner = models.ForeignKey(User, blank=False)
    tenancy = models.ForeignKey(Tenancy, blank=False)
    start_date = DatePickerField(blank=False)
    end_date = DatePickerField(blank=False)
    price = models.FloatField(blank=False)

    def __str__(self):
        return self.price

class TransactionCategory(models.Model):
    name = models.CharField(max_length=35, blank=False, unique=True)
    hmrc_code = models.CharField(max_length=2, unique=True)
    description = models.CharField(max_length=120, blank=False)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    owner = models.ForeignKey(User, blank=False)
    date = DatePickerField(blank=False)
    amount = models.FloatField(blank=False)
    building = models.ForeignKey(Building, blank=False)
    tenancy = models.ForeignKey(Tenancy)
    person = models.ForeignKey(Person)
    category = models.ForeignKey(TransactionCategory)
    description = models.CharField(max_length=120, blank=False)

    def __str__(self):
        return str(self.amount)

# Signals
def tenancy_calculate_on_init(instance, **kwargs):
    if instance.id:
        instance.calculate()
models.signals.post_init.connect(tenancy_calculate_on_init, Tenancy)

def building_calculate_on_init(instance, **kwargs):
    if instance.id:
        instance.calculate()
models.signals.post_init.connect(building_calculate_on_init, Building)
