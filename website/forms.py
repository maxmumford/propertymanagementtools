from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.conf import settings
from django.db.models import fields
import widgets
from models import Building, Room, Person, Tenancy, RentPrice, Transaction

from datetime import datetime

class CustomModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomModelForm, self).__init__(*args, **kwargs)

class BuildingForm(CustomModelForm):
    class Meta:
        model = Building
        fields = ['name', 'purchase_date']

class RoomForm(CustomModelForm):
    class Meta:
        model = Room
        fields = ['name', 'building']
        widgets = {
            'building': HiddenInput(),
        }

    def clean(self):
        if not self.is_valid():
            return
        cleaned_data = super(RoomForm, self).clean()

        # don't allow creation of room for a building that user does not own
        if not cleaned_data['building'].owner == self.request.user:
            raise ValidationError("You cannot create a room for a building that you do not own")

        return cleaned_data

class PersonForm(CustomModelForm):
    class Meta:
        model = Person
        fields = ['title', 'first_name', 'last_name', 'email', 'phone']


def date_spans_overlap(start_date_A, end_date_A, start_date_B, end_date_B):
    """ Checks if two date ranges overlap and returns False they don't """
    return start_date_A <= end_date_B and end_date_A >= start_date_B

class TenancyForm(CustomModelForm):
    price = forms.FloatField()

    class Meta:
        model = Tenancy
        fields = ['start_date', 'end_date', 'building', 'rooms', 'people']
        widgets = {
            'rooms': forms.widgets.SelectMultiple(attrs={'class': 'chained', 'data-chain-from': 'building', 'data-chain-endpoint': '/chaining/rooms_for_building'}),
        }

    def clean(self):
        if not self.is_valid():
            return
        cleaned_data = super(TenancyForm, self).clean()
        start = cleaned_data['start_date']
        end = cleaned_data['end_date']

        # prevent start date from being after end date
        if start > end:
            raise ValidationError('The start date must be before the end date')

        # prevent creation of overlapping tenancies for the same room
        conflicts = Tenancy.objects.filter(
            owner=self.request.user,
            start_date__lte=end,
            end_date__gte=start,
            rooms__contains=cleaned_data['rooms'],
        )
        if any(conflicts):
            raise ValidationError('One of your rooms is already occupied during this timespan! Check your existing tenancies for overlaps')
        
        # prevent creation of overlapping tenancies for a person
        conflicts = Tenancy.objects.filter(
            owner=self.request.user,
            people__contains=cleaned_data['people'],
            start_date__lte=end,
            end_date__gte=start
        )
        if any(conflicts):
            raise ValidationError('One of the tenants has an overlapping tenancy for this timespan')

        # prevent start date from being before building purchase date
        if start < cleaned_data['building'].purchase_date:
            raise ValidationError('The tenancy cannot start before the building purchase date (%s)' % cleaned_data['building'].purchase_date.strftime(settings.FRIENDLY_DATE))

        return cleaned_data

class RentPriceForm(CustomModelForm):
    class Meta:
        model = RentPrice
        fields = ['tenancy', 'start_date', 'end_date', 'price']

    def clean(self):
        self.is_valid()
        cleaned_data = super(RentPriceForm, self).clean()
        if cleaned_data['start_date'] > cleaned_data['end_date']:
            raise ValidationError('Start date is after end date')
        return cleaned_data

class TransactionForm(CustomModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'description', 'tenancy', 'building', 'person', 'category']
        widgets = {
            'building': forms.widgets.SelectMultiple(attrs={'class': 'chained', 'data-chain-from': 'tenancy', 'data-chain-endpoint': '/chaining/buildings_for_tenancy', \
                                                            'data-chain-autoselect': 'true', 'data-chain-disable': 'false'}),
        }

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=35)
    email = forms.EmailField(max_length=254)

    def save(self):
        if self.is_valid():
            user = User.objects.create_user(self.cleaned_data['username'], self.cleaned_data['email'], self.cleaned_data['password'], first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'])
