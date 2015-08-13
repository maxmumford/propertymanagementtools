from django.conf.urls import url

from . import views

urlpatterns = [
    # pages
    url(r'^$', views.index, name='index'),

    # properties
    url(r'^properties/$', views.properties, name='properties'),
    url(r'^property/(?P<property_id>[0-9]+)/$', views.property, name='property'),
    url(r'^property/new/$', views.property_new, name='property_new'),

    # users
    url(r'^user/new/$', views.user_new, name='user_new'),
    url(r'^user/login/$', 'django.contrib.auth.views.login', name='user_login', kwargs={'template_name': 'website/user_login.html'}),
    url(r'^user/logout/$', 'django.contrib.auth.views.logout', name='user_logout', kwargs={'next_page': '/'}),
    url(r'^user/change_password$', 'django.contrib.auth.views.password_change', name='user_password_change', kwargs={'template_name': 'website/user_password_change.html','post_change_redirect':'/',}),
    url(r'^user/premium/$', views.user_get_premium, name='user_get_premium'),

]
