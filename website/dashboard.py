from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import *
import calendar

# set decimal arithmatic context
context = getcontext()
#context.prec = 2
context.rounding=ROUND_HALF_UP

class Dashboard():
	"""
	Calculates the figures for the user's dashboard.
	Instantiate with the appropriate data, then call calculate
	Access the data with get_data. It returns a dict containing
	calculation results which can be passed directly to the index template
	"""

	# data sources
	tenancies = None
	transactions = None

	def __init__(self, tenancies, transactions):
		self.tenancies = tenancies
		self.transactions = transactions
		self.tenancy_summaries = []
		self._calculate_tenancy_summaries()

	def get_data(self):
		return self.tenancy_summaries

	def _calculate_tenancy_summaries(self):
		for tenancy in self.tenancies:
			total_paid = Decimal()
			total_charged = Decimal()

			# CALCULATE TOTAL CHARGED
			rent_prices_for_tenancy = tenancy.rentprice_set.all()
			start_date = tenancy.start_date
			end_date = tenancy.end_date
			now = datetime.date(datetime.now())
			if end_date > now:
				end_date = now

			# calculate total charged month by month
			date = start_date
			rent_prices_for_tenancy.order_by('start_date')

			for rent_price in rent_prices_for_tenancy:
				# set the end date to the rent_price end, or todays date, which ever is earlier
				rent_price_end = rent_price.end_date
				if now < rent_price_end:
					rent_price_end = now
				while date < rent_price_end:
					# work out rent per day and how many days to charge for this month
					days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
					rent_per_day = Decimal(str(rent_price.price)) / Decimal(str(days_in_month))
					if date.year == rent_price_end.year and date.month == rent_price_end.month:
						# calculating last month of tenancy
						chargable_days = rent_price_end.day
					elif date.day != 1:
						# calculating first month of tenancy
						chargable_days = days_in_month - date.day
					else:
						chargable_days = days_in_month
					rent_for_month = chargable_days * rent_per_day
					total_charged += rent_for_month
					# set the date to the first of the next month
					date = date + relativedelta(months=1)
					date = date.replace(day=1)
			# check if end date of tenancy is not the end of the month
			
			# CALCULATE TOTAL PAID
			transactions_for_tenancy = self.transactions.filter(tenancy=tenancy.id)
			for transaction in transactions_for_tenancy:
				total_paid += Decimal(transaction.amount)

			# create and cache TenancySummary
			self.tenancy_summaries.append(TenancySummary(tenancy, charged=total_charged, paid=total_paid))

class TenancySummary():
	""" represents the financial summary for a tenancy """

	def __init__(self, tenancy, charged=0, paid=0):
		self.tenancy = tenancy
		self._total_charged = charged
		self._total_paid = paid

	@property
	def arrears(self):
		return self.total_charged - self.total_paid

	@property
	def total_charged(self):
		return self._total_charged.quantize(Decimal('1.00'))

	@property
	def total_paid(self):
		return self._total_paid.quantize(Decimal('1.00'))

	def __str__(self):
		return str(self.tenancy) + ": Total charged is %(charged)s with %(paid)s having been paid, leaving %(arrears)s of arrears." % \
						{'charged': self.total_charged, 'paid': self.total_paid, 'arrears': self.arrears}
