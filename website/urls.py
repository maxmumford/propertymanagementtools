from django.conf.urls import url

from . import views

urlpatterns = [
    # pages
    url(r'^$', views.index, name='index'),

    # properties
    url(r'^properties/$', views.buildings, name='buildings'),
    url(r'^property/(?P<building_id>[0-9]+)/$', views.building, name='building'),
    url(r'^property/new/$', views.building_new, name='building_new'),

    # rooms
    url(r'^rooms/$', views.rooms, name='rooms'),
    url(r'^room/(?P<room_id>[0-9]+)/$', views.room, name='room'),
    url(r'^room/new/$', views.room_new, name='room_new'),

    # people
    url(r'^people/$', views.people, name='people'),
    url(r'^person/(?P<person_id>[0-9]+)/$', views.person, name='person'),
    url(r'^person/new/$', views.person_new, name='person_new'),

    # tenancies
    url(r'^tenancies/$', views.tenancies, name='tenancies'),
    url(r'^tenancy/(?P<tenancy_id>[0-9]+)/$', views.tenancy, name='tenancy'),
    url(r'^tenancies/new/$', views.tenancy_new, name='tenancy_new'),

    # transactions
    url(r'^transactions/$', views.transactions, name='transactions'),
    url(r'^transaction/(?P<transaction_id>[0-9]+)/$', views.transaction, name='transaction'),
    url(r'^transaction/new/$', views.transaction_new, name='transaction_new'),

    # users
    url(r'^user/new/$', views.user_new, name='user_new'),
    url(r'^user/login/$', 'django.contrib.auth.views.login', name='user_login', kwargs={'template_name': 'website/user_login.html'}),
    url(r'^user/logout/$', 'django.contrib.auth.views.logout', name='user_logout', kwargs={'next_page': '/'}),
    url(r'^user/change_password$', 'django.contrib.auth.views.password_change', name='user_password_change', kwargs={'template_name': 'website/user_password_change.html','post_change_redirect':'/',}),
    url(r'^user/premium/$', views.user_get_premium, name='user_get_premium'),

    # tax
    url(r'^tax/$', views.tax, name='tax'),

    # json
    url(r'^chaining/rooms_for_building/$', views.rooms_for_building, name='rooms_for_building'),
    url(r'^chaining/buildings_for_tenancy/$', views.buildings_for_tenancy, name='buildings_for_tenancy'),
]
