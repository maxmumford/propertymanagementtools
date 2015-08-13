from django.contrib import admin

from models import Property, Room, Person, Tenancy, RentPrice, TransactionCategory, Transaction

for model in (Property, Room, Person, Tenancy, RentPrice, TransactionCategory, Transaction):
	admin.site.register(model)
