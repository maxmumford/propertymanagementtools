import simplejson
import csv
from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import generic
from django.conf import settings
from django_tables2   import RequestConfig
from django.forms.models import modelformset_factory
from django.forms import HiddenInput

import models
import forms
import tables

def premium_required(view_function):
    def _wrapped_view_function(request, *args, **kwargs): 
        if request.user.is_authenticated() and bool(request.user.groups.filter(name__in=settings.PREMIUM_GROUP_NAME)) | request.user.is_superuser:
            return view_function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('user_get_premium'))
    return _wrapped_view_function

# pages
def index(request):
    if request.user.is_authenticated():
        return render(request, 'website/index.html')
    else:
        return render(request, 'website/index_anonymous.html')

def partial_dashboard(request):
    if request.user.is_authenticated():
        buildings = models.Building.objects.filter(owner=request.user)
        return render(request, 'website/partials/dashboard.html', {'buildings': buildings})
    else:
        raise PermissionDenied


# properties
@login_required
def buildings(request):
    building_list = models.Building.objects.filter(owner=request.user)
    return render(request, 'website/buildings.html', {'building_list': building_list})

@login_required
def building(request, building_id):
    building = get_object_or_404(models.Building, pk=building_id, owner=request.user)

    # get room form and prepopulate building_id field as the current building
    room_form = forms.RoomForm(request, initial={'building': building_id})
    return render(request, 'website/building.html', {'building': building, 'room_form': room_form})

@login_required
def building_new(request):
    if request.method == 'POST':
        form = forms.BuildingForm(request, request.POST)
        if form.is_valid():
            building = form.save(commit=False)
            building.owner = request.user
            building.save()
            return HttpResponseRedirect(reverse('building', args=(building.id,)))
        else:
            return render(request, 'website/building_new.html', {'form': form})
    else:
        form = forms.BuildingForm(request)

    return render(request, 'website/building_new.html', {'form': form})

# rooms
@login_required
def rooms(request):
    room_list = models.Room.objects.filter(owner=request.user)
    return render(request, 'website/rooms.html', {'room_list': room_list})

@login_required
def room(request, room_id):
    room = get_object_or_404(models.Room, pk=room_id, owner=request.user)
    return render(request, 'website/room.html', {'room': room})

@login_required
def room_new(request):
    """
    Create a new room and redirect to it's building
    """
    if request.method == 'POST':
        form = forms.RoomForm(request, request.POST)
        if form.is_valid():
            # check building is owned by user
            if form.cleaned_data['building'].owner == request.user:
                room = form.save(commit=False)
                room.owner = request.user
                room.save()
                return HttpResponseRedirect(reverse('building', args=(form.cleaned_data['building'].id,)))
        else:
            return render(request, 'website/room_new.html', {'form': form})
    else:
        form = forms.RoomForm(request)
        return render(request, 'website/room_new.html', {'form': form})

# people
@login_required
def people(request):
    people_list = models.Person.objects.filter(owner=request.user)
    return render(request, 'website/people.html', {'people_list': people_list})

@login_required
def person(request, person_id):
    person = get_object_or_404(models.Person, pk=person_id, owner=request.user)
    return render(request, 'website/person.html', {'person': person})

@login_required
def person_new(request):
    """
    Create a new person and redirect to people
    """
    if request.method == 'POST':
        form = forms.PersonForm(request, request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.owner = request.user
            person.save()
            return HttpResponseRedirect(reverse('people'))
        else:
            return render(request, 'website/person_new.html', {'form': form})
    else:
        form = forms.PersonForm(request)
        return render(request, 'website/person_new.html', {'form': form})

# tenancies
@login_required
def tenancies(request):
    tenancy_list = models.Tenancy.objects.filter(owner=request.user)
    return render(request, 'website/tenancies.html', {'tenancy_list': tenancy_list})

@login_required
def tenancy(request, tenancy_id):
    tenancy = get_object_or_404(models.Tenancy, pk=tenancy_id, owner=request.user)
    return render(request, 'website/tenancy.html', {'tenancy': tenancy})

@login_required
def tenancy_new(request):
    if request.method == 'POST':
        form = forms.TenancyForm(request, request.POST)
        if form.is_valid():
            tenancy = form.save(commit=False)
            tenancy.owner = request.user
            tenancy.save()
            form.save_m2m()

            # create corresponding RentPrice record
            rent_price_form = forms.RentPriceForm(request, {'tenancy': tenancy.id, 'start_date': tenancy.start_date, 'end_date': tenancy.end_date, 'price': request.POST['price']})
            if rent_price_form.is_valid():
                rent_price = rent_price_form.save(commit=False)
                rent_price.owner = request.user
                rent_price.save()
            else:
                raise Exception("Could not create RentPrice record: " + str(rent_price_form.errors))

            return HttpResponseRedirect(reverse('tenancy', args=(tenancy.id,)))
        else:
            return render(request, 'website/tenancy_new.html', {'form': form})
    else:
        form = forms.TenancyForm(request)
    return render(request, 'website/tenancy_new.html', {'form': form})

# transactions
def transactions(request):
    table = tables.TransactionTable(models.Transaction.objects.filter(owner=request.user).all())
    RequestConfig(request).configure(table)
    return render(request, 'website/transactions.html', {'table': table})

@login_required
def transaction(request, transaction_id):
    transaction = get_object_or_404(models.Transaction, pk=transaction_id, owner=request.user)
    return render(request, 'website/transaction.html', {'transaction': transaction})

@login_required
def transaction_new(request):
    if request.method == 'POST':
        form = forms.TransactionForm(request, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            transaction.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('transaction', args=(transaction.id,)))
        else:
            return render(request, 'website/transaction_new.html', {'form': form})
    else:
        form = forms.TransactionForm(request)
    return render(request, 'website/transaction_new.html', {'form': form})

# transaction import pending
@login_required
def transaction_import_pending_delete(request):
    """ Delete import pending and return empty 200 response """
    transaction_import_pending = get_object_or_404(models.TransactionImportPending, pk=request.GET.get('id', None), owner=request.user)
    transaction_import_pending.delete()
    return HttpResponseRedirect(reverse('transactions_bank_statement_review'))

@login_required
def transactions_bank_statement_upload(request):
    # if file already exists redirect to map
    if request.user.profile.bank_statement_file_exists:
        return HttpResponseRedirect(reverse('transactions_bank_statement_map'))

    # save uploaded file and redirect to mapping page
    if request.method == 'POST':
        form = forms.BankStatementUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect(reverse('transactions_bank_statement_map'))
        else:
            return render(request, 'website/transactions_bank_statement_upload.html', {'form': form})

    # render upload form
    else:
        form = forms.BankStatementUploadForm()
    return render(request, 'website/transactions_bank_statement_upload.html', {'form': form})

@login_required
def transactions_bank_statement_map(request):
    if request.user.profile.bank_statement_file_exists:
        # parse the file and render the mapping template with the column headers
        with open(request.user.profile.bank_statement_file_path, 'rb') as bank_statement_csv_file:
            try:
                csv_dialect = csv.Sniffer().sniff(bank_statement_csv_file.read(1024))
                bank_statement_csv_file.seek(0)
                csv_reader = csv.reader(bank_statement_csv_file, csv_dialect)
                for row in csv_reader:
                    return render(request, 'website/transactions_bank_statement_map.html', {'header_row': row})
            except csv.Error as e:
                messages.add_message(request, messages.ERROR, 'Sorry, we could not read that file. Please delete it try another format')
                return render(request, 'website/transactions_bank_statement_map.html')
    else:
        return HttpResponseRedirect(reverse('transactions_bank_statement_upload'))

@login_required
def transactions_bank_statement_import(request):
    # make sure a file exists
    if not request.user.profile.bank_statement_file_exists:
        return HttpResponseRedirect(reverse('transactions_bank_statement_upload'))

    # make sure the form was submitted
    if not request.POST:
        return HttpResponseRedirect(reverse('transactions_bank_statement_map'))

    # make sure each transaction field has been assigned to a header
    taken_fields = [value for key, value in request.POST.iteritems() if key != 'csrfmiddlewaretoken' and value != 'ignore']
    if 'date' not in taken_fields or \
        ('amount' not in taken_fields and 'amount_credit' not in taken_fields and 'amount_debit' not in taken_fields):
        messages.add_message(request, messages.ERROR, 'Not all fields have been mapped; please make sure at least the Date and Amount files have been mapped')
        return HttpResponseRedirect(reverse('transactions_bank_statement_map'))

    # import rows from file using mapping supplied in request.POST
    DATE_FORMATS = ['%d/%m/%Y', '%d/%m/%Y %I:%M:%S %p', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',\
                    '%Y/%m/%d', '%Y/%m/%d %I:%M:%S %p', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M',]
    with open(request.user.profile.bank_statement_file_path, 'rb') as bank_statement_csv_file:
        try:
            csv_dialect = csv.Sniffer().sniff(bank_statement_csv_file.read(1024))
            bank_statement_csv_file.seek(0)
            csv_reader = csv.reader(bank_statement_csv_file, csv_dialect)
            is_header = True
            header = None
            for row in csv_reader:
                if is_header:
                    header = row
                    is_header = False
                else:
                    # create ToImport record from row
                    to_import_data = dict.fromkeys(['date', 'amount', 'amount_debit', 'amount_credit', 'description'])

                    for column_number in range(0, len(row)):
                        column_header = header[column_number]
                        corresponding_field_name = request.POST[column_header]

                        for data_field_name in to_import_data.keys():
                            if corresponding_field_name == data_field_name:
                                to_import_data[data_field_name] = row[column_number]

                                # parse date
                                if corresponding_field_name == 'date':
                                    parsed_date = None
                                    for date_format in DATE_FORMATS:
                                        try:
                                            parsed_date = datetime.strptime(row[column_number], date_format)
                                            break
                                        except ValueError:
                                            pass
                                    if parsed_date == None:
                                         ValueError('Cold not parse the date %s' % row[column_number])
                                    else:
                                        to_import_data[data_field_name] = datetime.strftime(parsed_date, '%Y-%m-%d')
                                break

                    # handle amount credit and debit
                    if to_import_data['amount_debit'] and not to_import_data['amount']:
                        to_import_data['amount'] = abs(float(to_import_data['amount_debit']))
                    if to_import_data['amount_credit'] and not to_import_data['amount']:
                        to_import_data['amount'] = abs(float(to_import_data['amount_credit']))

                    del(to_import_data['amount_debit'])
                    del(to_import_data['amount_credit'])

                    # save the row
                    to_import_data['owner'] = request.user
                    transaction_import_pending = models.TransactionImportPending(**to_import_data)
                    transaction_import_pending.save()
        except csv.Error as e:
            messages.add_message(request, messages.ERROR, 'Sorry, we could not read that file. Please delete it try another format')
            return render(request, 'website/transactions_bank_statement_import.html')
        except ValueError as e:
            messages.add_message(request, messages.ERROR, e.message)
            return render(request, 'website/transactions_bank_statement_import.html')

    # delete the bank statement file and redirect to review
    request.user.profile.bank_statement_delete()
    return HttpResponseRedirect(reverse('transactions_bank_statement_review'))

@login_required
def transactions_bank_statement_review(request):
    """ Allow the user to change the data in the transactions before importing """

    def class_gen_with_kwarg(cls, **additionalkwargs):
        """
        class generator for subclasses with additional 'stored' parameters (in a closure)
        This is required to use a modelformset_factory with a form that needs additional 
        initialization parameters (see http://stackoverflow.com/questions/622982/django-passing-custom-form-parameters-to-formset)
        """
        class ClassWithKwargs(cls):
            def __init__(self, *args, **kwargs):
                kwargs.update(additionalkwargs)
                super(ClassWithKwargs, self).__init__(*args, **kwargs)
        return ClassWithKwargs

    # create the formset
    pending_imports = models.TransactionImportPending.objects.filter(owner=request.user)
    TransactionImportPendingFormset = modelformset_factory(models.TransactionImportPending, \
                                        form=class_gen_with_kwarg(forms.TransactionImportPendingForm, request=request), \
                                        fields=['date', 'amount', 'description', 'tenancy', 'building', 'person', 'category'],\
                                        extra=0)

    if request.method == 'POST':
        # save the user's changes
        formset = TransactionImportPendingFormset(request.POST)
        if formset.is_valid():
            formset.save()

            # convert transaction import pending to transactions
            if request.POST.get('import', False) != False:
                for record_data in formset.cleaned_data:
                    record_id = record_data.pop('id').id
                    record_data['owner'] = request.user
                    transaction = models.Transaction(**record_data)
                    transaction.save()
                    models.TransactionImportPending.objects.filter(owner=request.user, id=record_id).delete()

                # redirect to transactions
                return HttpResponseRedirect(reverse('transactions'))
        return render(request, 'website/transactions_bank_statement_review.html', {'formset': formset})
    else:
        # redirect to upload if no pending imports
        if not pending_imports:
            return HttpResponseRedirect(reverse('transactions_bank_statement_upload'))

        # show the unbound formset with all their pending imports
        formset = TransactionImportPendingFormset(queryset=pending_imports)
        return render(request, 'website/transactions_bank_statement_review.html', {'formset': formset})

@login_required
def transactions_bank_statement_delete(request):
    if request.user.profile.bank_statement_file_exists:
        request.user.profile.bank_statement_delete()
    return HttpResponseRedirect(reverse('transactions_bank_statement_upload'))

# users
def user_new(request):
    if request.method == 'POST':
        form = forms.UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('user_login'))
        else:
            return render(request, 'website/user_new.html', {'form': form})
    else:
        form = forms.UserForm()
    return render(request, 'website/user_new.html', {'form': form})

def user_get_premium(request):
    return render(request, 'website/user_get_premium.html')

def tax(request):
    all_transaction_categories = models.TransactionCategory.objects.exclude(hmrc_code__isnull=True).all()
    transaction_category_totals = {}
    for transaction_category in all_transaction_categories:
        transaction_category_totals[transaction_category] = transaction_category.sum_of_transactions(request.user)
    return render(request, 'website/tax.html', {'transaction_category_totals': transaction_category_totals})

# json
def rooms_for_building(request):
    building_id = request.GET.get('building_id')
    if not building_id:
        raise Http404
    rooms = models.Room.objects.filter(owner=request.user, building=building_id)
    rooms_list = {}
    for room in rooms:
        rooms_list[room.id] = str(room)
    return HttpResponse(simplejson.dumps(rooms_list), content_type="application/json")

def buildings_for_tenancy(request):
    tenancy_id = request.GET.get('tenancy_id')
    if not tenancy_id:
        raise Http404
    if tenancy_id == '0':
        buildings = models.Building.objects.filter(owner=request.user).all()
        building_list = {}
        for building in buildings:
            building_list[building.id] = str(building)
    else:
        tenancy = models.Tenancy.objects.get(owner=request.user, id=tenancy_id)
        building_list = {tenancy.building.id: str(tenancy.building)}
    return HttpResponse(simplejson.dumps(building_list), content_type="application/json")

def people_for_tenancy(request):
    tenancy_id = request.GET.get('tenancy_id')
    if not tenancy_id:
        raise Http404
    if tenancy_id == '0':
        people = models.Person.objects.filter(owner=request.user).all()
        people_list = {}
        for person in people:
            people_list[person.id] = str(person)
    else:
        tenancy = models.Tenancy.objects.get(owner=request.user, id=tenancy_id)
        people_list = {}
        for person in tenancy.people.all():
            people_list[person.id] = str(person)
    return HttpResponse(simplejson.dumps(people_list), content_type="application/json")
