from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import Property
from forms import PropertyForm, UserForm
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

# properties
@login_required
def properties(request):
    property_list = Property.objects.filter(owner=request.user)
    return render(request, 'website/properties.html', {'property_list': property_list})

@login_required
def property(request, property_id):
    property = get_object_or_404(Property, pk=property_id, owner=request.user)
    return render(request, 'website/property.html', {'property': property})

@login_required
def property_new(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            return HttpResponseRedirect(reverse('property', args=(property.id,)))
    else:
        form = PropertyForm()

    return render(request, 'website/property_new.html', {'form': form})

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
