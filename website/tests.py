from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from forms import TenancyForm, RentPriceForm
import datetime

class TenancyMethodTests(TestCase):

    def test_start_date_after_end_date(self):
        """
        Create should raise an exception when trying to create a tenancy
        with a start_date after the end_date
        """
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() - datetime.timedelta(days=30)
        tenancy = TenancyForm({'start_date': start_date, 'end_date': end_date})
        self.assertRaises(ValidationError, tenancy.clean)

class RentPriceMethodTests(TestCase):

    def test_start_date_after_end_date(self):
        """
        Create should raise an exception when trying to create a tenancy
        with a start_date after the end_date
        """
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() - datetime.timedelta(days=30)
        rent_price = RentPriceForm({'start_date': start_date, 'end_date': end_date})
        self.assertRaises(ValidationError, rent_price.clean)
