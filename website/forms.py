from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.conf import settings
import django.db.models
from django.db.models import fields
import widgets
from models import TransactionImportPending, Building, Room, Person, Tenancy, RentPrice, Transaction

class CustomModelForm(forms.ModelForm):
    """ 
    Caches the request object for each form and for each field,
    checks if the field has an owner field and limits the queryset
    to records where owner = request.user, thereby sandboxing
    the user data in forms.
    """
    def __init__(self, request, *args, **kwargs):
        # cache request and call super
        self.request = request
        init_result = super(CustomModelForm, self).__init__(*args, **kwargs)

        # go through each field
        for field_name, field_widget in self.fields.iteritems():
            # find the model field definition
            model_field = getattr(self.Meta.model, field_name, None)
            if model_field:
                # check if it has a related model
                related_model = getattr(model_field.field, 'related_model', None)
                if related_model:
                    # check if it has an owner field
                    owner_field = getattr(related_model, 'owner', None)
                    if owner_field:
                        # filter field objects by owner = logged in user
                        field_widget.queryset = related_model.objects.filter(owner=request.user)

        return init_result

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

    def __init__(self, *args, **kwargs):
        init_result = super(TenancyForm, self).__init__(*args, **kwargs)
        rooms_attrs = {'class': 'chained', 'data-chain-from': 'building', 'data-chain-endpoint': '/chaining/rooms_for_building'}
        self.fields['rooms'].widget.attrs.update(rooms_attrs)
        return init_result

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
    def __init__(self, *args, **kwargs):
        init_result = super(TransactionForm, self).__init__(*args, **kwargs)
        building_attrs = {'class': 'chained', 'data-chain-from': 'tenancy', 'data-chain-endpoint': '/chaining/buildings_for_tenancy', 'data-chain-start-enabled': 'true'}
        self.fields['building'].widget.attrs.update(building_attrs)
        person_attrs = {'class': 'chained', 'data-chain-from': 'tenancy', 'data-chain-endpoint': '/chaining/people_for_tenancy', 'data-chain-start-enabled': 'true'}
        self.fields['person'].widget.attrs.update(person_attrs)
        return init_result

    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'description', 'tenancy', 'building', 'person', 'category']

class TransactionImportPendingForm(CustomModelForm):
    def __init__(self, *args, **kwargs):
        init_result = super(TransactionImportPendingForm, self).__init__(*args, **kwargs)
        building_attrs = {'class': 'chained', 'data-chain-from': 'tenancy', 'data-chain-endpoint': '/chaining/buildings_for_tenancy', 'data-chain-start-enabled': 'true'}
        self.fields['building'].widget.attrs.update(building_attrs)
        person_attrs = {'class': 'chained', 'data-chain-from': 'tenancy', 'data-chain-endpoint': '/chaining/people_for_tenancy', 'data-chain-start-enabled': 'true'}
        self.fields['person'].widget.attrs.update(person_attrs)
        return init_result

    class Meta:
        model = TransactionImportPending
        fields = ['date', 'amount', 'description', 'tenancy', 'building', 'person', 'category']
        widgets = {
            'date': HiddenInput(),
            'amount': HiddenInput(),
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

class BankStatementUploadForm(forms.Form):
    bank_statement_file = forms.FileField(label='Select your CSV bank statement', help_text='Maximum file size is 42 megabytes')

    def save(self, user):
        # raise exception if bank statement already exists
        if user.profile.bank_statement_file_exists:
            raise ValidationError('Bank statement already exists, please delete it before uploading a new one')

        # save bank statement
        user.profile.bank_statement_save(self.cleaned_data['bank_statement_file'])
