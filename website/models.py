from django.db import models
from django.contrib.auth.models import User

TITLE_CHOICES = (
    ('MR', 'Mr.'),
    ('MRS', 'Mrs.'),
    ('MS', 'Ms.'),
)

class House(models.Model):
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
    house = models.ForeignKey(House, blank=False)

    def __str__(self):
        return self.name

class Person(models.Model):
    owner = models.ForeignKey(User, blank=False)
    title = models.CharField(max_length=35, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=35, blank=False)
    last_name = models.CharField(max_length=35, blank=False)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=25)

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.full_name()

class Tenancy(models.Model):
    owner = models.ForeignKey(User, blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    rooms = models.ManyToManyField(Room, blank=False)
    people = models.ManyToManyField(Person, blank=False)

class RentPrice(models.Model):
    owner = models.ForeignKey(User, blank=False)
    tenancy = models.ForeignKey(Tenancy, blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    price = models.FloatField(blank=False)

    def __str__(self):
        return self.price

class TransactionCategory(models.Model):
    name = models.CharField(max_length=35, blank=False)
    hmrc_code = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    owner = models.ForeignKey(User, blank=False)
    datetime = models.DateTimeField(blank=False)
    amount = models.FloatField(blank=False)
    tenancy = models.ForeignKey(Tenancy)
    house = models.ForeignKey(House, blank=False)
    category = models.ForeignKey(TransactionCategory)

    def __str__(self):
        return self.amount
