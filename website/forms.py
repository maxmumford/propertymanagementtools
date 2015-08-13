from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.conf import settings

from models import Property, Room, Person, Tenancy, RentPrice

from datetime import datetime

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'property']
        widgets = {
            'property': HiddenInput(),
        }

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['title', 'first_name', 'last_name', 'email', 'phone']

class TenancyForm(forms.ModelForm):
    class Meta:
        model = Tenancy
        fields = ['start_date', 'end_date', 'rooms', 'people']

    def clean(self):
        if not self.is_valid():
            return
        cleaned_data = super(TenancyForm, self).clean()

        # prevent start date from being after end date
        if cleaned_data['start_date'] > cleaned_data['end_date']:
            raise ValidationError('The start date must be before the end date')

        # prevent creation of overlapping tenancies
        overlapping_tenancies = Tenancy.objects.filter(start_date__gte=cleaned_data['start_date'], start_date__lte=cleaned_data['end_date']) | \
                                  Tenancy.objects.filter(end_date__gte=cleaned_data['start_date'], end_date__lte=cleaned_data['end_date'])
        if len(overlapping_tenancies) > 0:
            raise ValidationError('You already have a tenancy for the period %s to %s' % (overlapping_tenancies[0].start_date.strftime(settings.FRIENDLY_DATE), overlapping_tenancies[0].end_date.strftime(settings.FRIENDLY_DATE)))
        return cleaned_data

class RentPriceForm(forms.ModelForm):
    class Meta:
        model = RentPrice
        fields = ['tenancy', 'start_date', 'end_date', 'price']

    def clean(self):
        self.is_valid()
        cleaned_data = super(RentPriceForm, self).clean()
        if cleaned_data['start_date'] > cleaned_data['end_date']:
            raise ValidationError('Start date is after end date')
        return cleaned_data

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=35)
    email = forms.EmailField(max_length=254)

    def save(self):
        if self.is_valid():
            user = User.objects.create_user(self.cleaned_data['username'], self.cleaned_data['email'], self.cleaned_data['password'], first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'])
