from django.db import models
from django.contrib.auth.models import User
from fields import DatePickerField

TITLE_CHOICES = (
    ('MR', 'Mr.'),
    ('MRS', 'Mrs.'),
    ('MS', 'Ms.'),
)

class Property(models.Model):
    owner = models.ForeignKey(User, blank=False)
    name = models.CharField(max_length=35, blank=False)
    address_line_1 = models.CharField(max_length=45)
    address_line_2 = models.CharField(max_length=45)
    city = models.CharField(max_length=35)
    county = models.CharField(max_length=35)
    postcode = models.CharField(max_length=35)
    country = models.CharField(max_length=35)

    def __str__(self):
        return self.name

class Room(models.Model):
    owner = models.ForeignKey(User, blank=False)
    name = models.CharField(max_length=35, blank=False)
    property = models.ForeignKey(Property, blank=False)

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
    owner = models.ForeignKey(User, blank=False)
    start_date = DatePickerField(blank=False)
    end_date = DatePickerField(blank=False)
    property = models.ForeignKey(Property, blank=False)
    rooms = models.ManyToManyField(Room, blank=False)
    people = models.ManyToManyField(Person, blank=False)

    def __str__(self):
        return self.people.all()[0].first_name + ' in ' + self.property.name

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
    tenancy = models.ForeignKey(Tenancy)
    property = models.ForeignKey(Property, blank=False)
    category = models.ForeignKey(TransactionCategory)

    def __str__(self):
        return self.amount
