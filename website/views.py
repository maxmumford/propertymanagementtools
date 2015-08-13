from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import House
from forms import HouseForm, UserForm
from django.contrib.auth.decorators import login_required, user_passes_test
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

# houses
@login_required
def houses(request):
    house_list = House.objects.filter(owner=request.user)
    return render(request, 'website/houses.html', {'house_list': house_list})

@login_required
def house(request, house_id):
    house = get_object_or_404(House, pk=house_id, owner=request.user)
    return render(request, 'website/house.html', {'house': house})

@login_required
def house_new(request):
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            house = form.save(commit=False)
            house.owner = request.user
            house.save()
            return HttpResponseRedirect(reverse('house', args=(house.id,)))
    else:
        form = HouseForm()

    return render(request, 'website/house_new.html', {'form': form})

# users
def user_new(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('user_login'))
    else:
        form = UserForm()
    return render(request, 'website/user_new.html', {'form': form})

def user_get_premium(request):
    return render(request, 'website/user_get_premium.html')
