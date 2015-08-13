from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from models import Property
from forms import TenancyForm, RentPriceForm
from views import property_new, room_new

import datetime

TEST_VALUES = {
    'user_username': 'tom',
    'other_user_username': 'sam',
    'property_name': 'Manor Road',
    'room_name': '1',
}

class TestCaseStandardUser(TestCase):

    def setUp(self):
        """
        Get the standard test user and set up a factory
        """
        self.factory = RequestFactory()

        # set up standard user for us to use
        try:
            self.user = User.objects.get(username=TEST_VALUES['user_username'])
        except User.DoesNotExist:
            self.user = User.objects.create_user(username=TEST_VALUES['user_username'], email='tom@example.com', password='super_secret_password')

        # set up another user for us to test security against
        try:
            self.other_user = User.objects.get(username=TEST_VALUES['other_user_username'])
        except User.DoesNotExist:
            self.other_user = User.objects.create_user(username=TEST_VALUES['other_user_username'], email='sam@example.com', password='mega_secret_password')

class PropertyMethodTests(TestCaseStandardUser):

    def test_create_property(self):
        """ Create a standard Property """
        request = self.factory.post(reverse('property_new'), {'name': TEST_VALUES['property_name']})
        request.user = self.user
        response = property_new(request)
        prop = Property.objects.filter(name=TEST_VALUES['property_name'])
        self.assertEqual(len(prop), 1)

class TenancyMethodTests(TestCaseStandardUser):

    def test_start_date_after_end_date(self):
        """
        Create should raise an exception when trying to create a tenancy
        with a start_date after the end_date
        """
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() - datetime.timedelta(days=30)
        tenancy = TenancyForm({'start_date': start_date, 'end_date': end_date})
        self.assertRaises(ValidationError, tenancy.clean)

class RentPriceMethodTests(TestCaseStandardUser):

    def test_start_date_after_end_date(self):
        """
        Create should raise an exception when trying to create a tenancy
        with a start_date after the end_date
        """
        start_date = timezone.now() + datetime.timedelta(days=30)
        end_date = timezone.now() - datetime.timedelta(days=30)
        rent_price = RentPriceForm({'start_date': start_date, 'end_date': end_date})
        self.assertRaises(ValidationError, rent_price.clean)
