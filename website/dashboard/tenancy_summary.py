from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import *
import calendar

# set decimal arithmatic context
context = getcontext()
context.rounding=ROUND_HALF_UP

class TenancySummary():

    def __init__(self, tenancy, transactions):
        self._total_charged = Decimal('0')
        self._total_paid = Decimal('0')

        self._arrears_total_charged = Decimal('0')

        self.date = tenancy.start_date
        self.tenancy = tenancy
        self.transactions = transactions
        self.rent_prices = tenancy.rentprice_set.all()

    @property
    def arrears(self):
        return (self._arrears_total_charged - self._total_paid).quantize(Decimal('1.00'))

    @property
    def total_charged(self):
        return self._total_charged.quantize(Decimal('1.00'))

    @property
    def total_paid(self):
        return self._total_paid.quantize(Decimal('1.00'))

    def __str__(self):
        return str(self.tenancy) + ": Total charged is %(charged)s with %(paid)s having been paid, leaving %(arrears)s of arrears." % \
                        {'charged': self.total_charged, 'paid': self.total_paid, 'arrears': self.arrears}

    def calculate(self):
        self._calculate_total_charged()
        self._calculate_total_paid()

    def _calculate_total_charged(self):
        # loop from month to month totting up the total_charged until the last month of the tenancy has been processed
        while not self._all_months_processed():
            # if we are calculating the last month, save the total paid and charged figures for arrears
            # because the tenant has until the end of the month to pay them
            if self._is_last_month():
                self._arrears_total_charged = self._total_charged

            # calculate month
            chargable_days_for_month = self._get_chargable_days_for_month(self.date, self.tenancy.end_date)
            for day in range(1, chargable_days_for_month + 1):
                daily_rent = self._get_rent_for_day(self.date.replace(day=day))
                self._total_charged += Decimal(str(daily_rent))

            self._next_month()

    def _calculate_total_paid(self):
        # calculate total payments made by the tenant
        for transaction in self.transactions:
            self._total_paid += Decimal(transaction.amount)

    def _get_rent_for_day(self, date):
        # calculate the rent for the day of date based on rent_price records
        rent_for_day = None
        days_in_month = self._get_days_in_month(date)
        for rent_price in self.rent_prices:
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
        if date.year == self.tenancy.end_date.year and date.month == self.tenancy.end_date.month:
            # last month of the tenancy
            chargable_days = self.tenancy.end_date.day - (date.day - 1)
        else:
            # either first month or middle month
            chargable_days = self._get_days_in_month(date) - (date.day - 1)
        return chargable_days

    def _get_days_in_month(self, date):
        # return number of days in the month
        return calendar.monthrange(date.year, date.month)[1]

    def _get_end_year_month(self):
        end_month = self.tenancy.end_date.month
        end_year = self.tenancy.end_date.year
        now = datetime.now()
        if now.date() < self.tenancy.end_date:
            end_month = now.month
            end_year = now.year
        return (end_year, end_month)

    def _all_months_processed(self):
        # stop processing tenancy when self.date is in the same month as the tenancy end date, or now, whichever is sooner
        end_year, end_month = self._get_end_year_month()
        return (self.date.year <= end_year and self.date.month <= end_month) == False

    def _is_last_month(self):
        end_year, end_month = self._get_end_year_month()
        return self.date.year == end_year and self.date.month == end_month

    def _next_month(self):
        # increments self.date to be the first of the next month
        self.date = self.date + relativedelta(months=1)
        self.date = self.date.replace(day=1)

class InvalidDataError(Exception):
    pass
