from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from models import House, Tenancy, RentPrice

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['name']

class TenancyForm(forms.ModelForm):
    class Meta:
        model = Tenancy
        fields = ['start_date', 'end_date', 'rooms', 'people']

    def clean(self):
        self.is_valid()
        cleaned_data = super(TenancyForm, self).clean()
        if cleaned_data['start_date'] > cleaned_data['end_date']:
            raise ValidationError('Start date is after end date')
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
