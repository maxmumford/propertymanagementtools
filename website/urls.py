from django.conf.urls import url

from . import views

urlpatterns = [
    # pages
    url(r'^$', views.index, name='index'),

    # houses
    url(r'^houses/$', views.houses, name='houses'),
    url(r'^house/(?P<house_id>[0-9]+)/$', views.house, name='house'),
    url(r'^house/new/$', views.house_new, name='house_new'),

    # users
    url(r'^user/new/$', views.user_new, name='user_new'),
    url(r'^user/login/$', 'django.contrib.auth.views.login', name='user_login', kwargs={'template_name': 'website/user_login.html'}),
    url(r'^user/logout/$', 'django.contrib.auth.views.logout', name='user_logout', kwargs={'next_page': '/'}),
    url(r'^user/change_password$', 'django.contrib.auth.views.password_change', name='user_password_change', kwargs={'template_name': 'website/user_password_change.html','post_change_redirect':'/',}),
    url(r'^user/premium/$', views.user_get_premium, name='user_get_premium'),

]
