from django.contrib import admin

from models import Building, Room, Person, Tenancy, RentPrice, TransactionCategory, Transaction

for model in (Building, Room, Person, Tenancy, RentPrice, TransactionCategory, Transaction):
	admin.site.register(model)
