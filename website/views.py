from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import Property, Room, Person, Tenancy
from forms import PropertyForm, RoomForm, PersonForm, UserForm, TenancyForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import generic
from django.conf import settings

def premium_required(view_function):
    def _wrapped_view_function(request, *args, **kwargs): 
        if request.user.is_authenticated() and bool(request.user.groups.filter(name__in=settings.PREMIUM_GROUP_NAME)) | request.user.is_superuser:
            return view_function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('user_get_premium'))
    return _wrapped_view_function

# pages
def index(request):
    return render(request, 'website/index.html')

# properties
@login_required
def properties(request):
    property_list = Property.objects.filter(owner=request.user)
    return render(request, 'website/properties.html', {'property_list': property_list})

@login_required
def property(request, property_id):
    prop = get_object_or_404(Property, pk=property_id, owner=request.user)

    # get room form and prepopulate property_id field as the current property
    room_form = RoomForm(initial={'property': property_id})
    return render(request, 'website/property.html', {'property': prop, 'room_form': room_form})

@login_required
def property_new(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request=request)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()
            return HttpResponseRedirect(reverse('property', args=(prop.id,)))
        else:
            return render(request, 'website/property_new.html', {'form': form})
    else:
        form = PropertyForm()

    return render(request, 'website/property_new.html', {'form': form})

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
    Create a new room and redirect to it's property
    """
    if request.method == 'POST':
        form = RoomForm(request.POST, request=request)
        if form.is_valid():
            # check property is owned by user
            if form.cleaned_data['property'].owner == request.user:
                room = form.save(commit=False)
                room.owner = request.user
                room.save()
                return HttpResponseRedirect(reverse('property', args=(form.cleaned_data['property'].id,)))
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
        """Return the last five published questions."""
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
            return HttpResponseRedirect(reverse('tenancy', args=(tenancy.id,)))
        else:
            return render(request, 'website/tenancy_new.html', {'form': form})
    else:
        form = TenancyForm()
    return render(request, 'website/tenancy_new.html', {'form': form})

# users
def user_new(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request=request)
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
