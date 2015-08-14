# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import website

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=35)),
                ('address_line_1', models.CharField(max_length=45)),
                ('address_line_2', models.CharField(max_length=45)),
                ('city', models.CharField(max_length=35)),
                ('county', models.CharField(max_length=35)),
                ('postcode', models.CharField(max_length=35)),
                ('country', models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=35)),
                ('first_name', models.CharField(max_length=35)),
                ('last_name', models.CharField(max_length=35)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='RentPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', website.fields.DatePickerField()),
                ('end_date', website.fields.DatePickerField()),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=35)),
                ('property', models.ForeignKey(to='website.Property')),
            ],
        ),
        migrations.CreateModel(
            name='Tenancy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', website.fields.DatePickerField()),
                ('end_date', website.fields.DatePickerField()),
                ('people', models.ManyToManyField(to=b'website.Person')),
                ('rooms', models.ManyToManyField(to=b'website.Room')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', website.fields.DatePickerField()),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TransactionCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=35,)),
                ('hmrc_code', models.CharField(unique=True, max_length=2)),
                ('description', models.CharField(max_length=120)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(to='website.TransactionCategory'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='property',
            field=models.ForeignKey(to='website.Property'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='tenancy',
            field=models.ForeignKey(to='website.Tenancy'),
        ),
        migrations.AddField(
            model_name='rentprice',
            name='tenancy',
            field=models.ForeignKey(to='website.Tenancy'),
        ),
        migrations.AddField(
            model_name='property',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='person',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rentprice',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transaction',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='person',
            name='title',
            field=models.CharField(max_length=35, choices=[(b'MR', b'Mr.'), (b'MRS', b'Mrs.'), (b'MS', b'Ms.')]),
        ),
        migrations.AddField(
            model_name='tenancy',
            name='property',
            field=models.ForeignKey(default='', to='website.Property'),
        ),
    ]
