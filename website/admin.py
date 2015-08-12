from django.contrib import admin

from models import House, Room, Person, Tenancy, RentPrice, TransactionCategory, Transaction

for model in (House, Room, Person, Tenancy, RentPrice, TransactionCategory, Transaction):
	admin.site.register(model)
