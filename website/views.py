import simplejson

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import generic
from django.conf import settings

from models import Building, Room, Person, Tenancy, RentPrice, Transaction, TransactionCategory
from forms import BuildingForm, RoomForm, PersonForm, UserForm, TenancyForm, RentPriceForm, TransactionForm

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
        buildings = Building.objects.filter(owner=request.user)
        return render(request, 'website/index.html', {'buildings': buildings})
    else:
        return render(request, 'website/index_anonymous.html')

# properties
@login_required
def buildings(request):
    building_list = Building.objects.filter(owner=request.user)
    return render(request, 'website/buildings.html', {'building_list': building_list})

@login_required
def building(request, building_id):
    building = get_object_or_404(Building, pk=building_id, owner=request.user)

    # get room form and prepopulate building_id field as the current building
    room_form = RoomForm(initial={'building': building_id})
    return render(request, 'website/building.html', {'building': building, 'room_form': room_form})

@login_required
def building_new(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST, request=request)
        if form.is_valid():
            building = form.save(commit=False)
            building.owner = request.user
            building.save()
            return HttpResponseRedirect(reverse('building', args=(building.id,)))
        else:
            return render(request, 'website/building_new.html', {'form': form})
    else:
        form = BuildingForm()

    return render(request, 'website/building_new.html', {'form': form})

# rooms
@login_required
def rooms(request):
    room_list = Room.objects.filter(owner=request.user)
    return render(request, 'website/rooms.html', {'room_list': room_list})

@login_required
def room(request, room_id):
    room = get_object_or_404(Room, pk=room_id, owner=request.user)
    return render(request, 'website/room.html', {'room': room})

@login_required
def room_new(request):
    """
    Create a new room and redirect to it's building
    """
    if request.method == 'POST':
        form = RoomForm(request.POST, request=request)
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
        form = RoomForm()
        return render(request, 'website/room_new.html', {'form': form})

# people
@login_required
def people(request):
    people_list = Person.objects.filter(owner=request.user)
    return render(request, 'website/people.html', {'people_list': people_list})

@login_required
def person(request, person_id):
    person = get_object_or_404(Person, pk=person_id, owner=request.user)
    return render(request, 'website/person.html', {'person': person})

@login_required
def person_new(request):
    """
    Create a new person and redirect to people
    """
    if request.method == 'POST':
        form = PersonForm(request.POST, request=request)
        if form.is_valid():
            person = form.save(commit=False)
            person.owner = request.user
            person.save()
            return HttpResponseRedirect(reverse('people'))
        else:
            return render(request, 'website/person_new.html', {'form': form})
    else:
        form = PersonForm()
        return render(request, 'website/person_new.html', {'form': form})

# tenancies
class tenancies(generic.ListView):
    template_name = 'website/tenancies.html'
    context_object_name = 'tenancy_list'

    def get_queryset(self):
        return Tenancy.objects.filter(owner=self.request.user)

class tenancy(generic.DetailView):
    model = Tenancy
    template_name = 'website/tenancy.html'

@login_required
def tenancy_new(request):
    if request.method == 'POST':
        form = TenancyForm(request.POST, request=request)
        if form.is_valid():
            tenancy = form.save(commit=False)
            tenancy.owner = request.user
            tenancy.save()
            form.save_m2m()

            # create corresponding RentPrice record
            rent_price_form = RentPriceForm({'tenancy': tenancy.id, 'start_date': tenancy.start_date, 'end_date': tenancy.end_date, 'price': request.POST['price']})
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
        form = TenancyForm()
    return render(request, 'website/tenancy_new.html', {'form': form})

# transactions
class transactions(generic.ListView):
    template_name = 'website/transactions.html'
    context_object_name = 'transaction_list'

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user)

class transaction(generic.DetailView):
    model = Transaction
    template_name = 'website/transaction.html'

@login_required
def transaction_new(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request=request)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            transaction.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('transaction', args=(transaction.id,)))
        else:
            return render(request, 'website/transaction_new.html', {'form': form})
    else:
        form = TransactionForm()
    return render(request, 'website/transaction_new.html', {'form': form})

# users
def user_new(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('user_login'))
        else:
            return render(request, 'website/user_new.html', {'form': form})
    else:
        form = UserForm()
    return render(request, 'website/user_new.html', {'form': form})

def user_get_premium(request):
    return render(request, 'website/user_get_premium.html')

def tax(request):
    all_transaction_categories = TransactionCategory.objects.exclude(hmrc_code__isnull=True).all()
    transaction_category_totals = {}
    for transaction_category in all_transaction_categories:
        transaction_category_totals[transaction_category] = transaction_category.sum_of_transactions(request.user)
    return render(request, 'website/tax.html', {'transaction_category_totals': transaction_category_totals})

# json
def rooms_for_building(request):
    building_id = request.GET.get('building_id')
    if not building_id:
        raise Http404
    rooms = Room.objects.filter(owner=request.user, building=building_id)
    rooms_list = {}
    for room in rooms:
        rooms_list[room.id] = str(room)
    return HttpResponse(simplejson.dumps(rooms_list), content_type="application/json")

def buildings_for_tenancy(request):
    tenancy_id = request.GET.get('tenancy_id')
    if not tenancy_id:
        raise Http404
    if tenancy_id == '0':
        buildings = Building.objects.filter(owner=request.user).all()
        building_list = {}
        for building in buildings:
            building_list[building.id] = str(building)
    else:
        tenancy = Tenancy.objects.get(owner=request.user, id=tenancy_id)
        building_list = {tenancy.building.id: str(tenancy.building)}
    return HttpResponse(simplejson.dumps(building_list), content_type="application/json")
