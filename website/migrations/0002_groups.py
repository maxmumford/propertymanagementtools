# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.contrib.auth.models import Group

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

def add_group_permissions(*args, **kwargs):
    # create premium and free groups
    group, created = Group.objects.get_or_create(name=settings.PREMIUM_GROUP_NAME)
    group, created = Group.objects.get_or_create(name=settings.FREE_GROUP_NAME) 

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_group_permissions),
    ]
