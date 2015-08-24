from decimal import Decimal

class Invoice():
	def __init__(self, date, end_date, amount_due):
		if not isinstance(amount_due, Decimal):
			raise TypeError('Need Decimal')
		self._date = date
		self._end_date = end_date
		self._amount_due = round(amount_due, 20)
		self._payments = {}

	def make_payment(self, transaction, amount):
		self._payments[transaction] = Decimal(str(amount))

	@property
	def date(self):
		return self._date

	@property
	def end_date(self):
		return self._end_date

	@property
	def amount_due(self):
		return Decimal(str(self._amount_due))

	@property
	def amount_paid(self):
		return Decimal(str(sum(self._payments.values())))

	@property
	def paid(self):
		return self.amount_paid >= self.amount_due

	@property
	def balance(self):
		return self.amount_due - self.amount_paid

	@property
	def in_surplus(self):
		return self.amount_paid > self.amount_due

	@property
	def in_deficit(self):
		return self.amount_due > self.amount_paid

	@property
	def surplus(self):
		if self.in_surplus:
			return self.amount_paid - self.amount_due
		else:
			return 0

	@property
	def deficit(self):
		if self.in_deficit:
			return self.amount_due - self.amount_paid
		else:
			return 0		
