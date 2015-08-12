# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='House',
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
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=35)),
                ('house', models.ForeignKey(to='website.House')),
            ],
        ),
        migrations.CreateModel(
            name='Tenancy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('people', models.ManyToManyField(to='website.Person')),
                ('rooms', models.ManyToManyField(to='website.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='TransactionCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=35)),
                ('hmrc_code', models.CharField(max_length=2)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(to='website.TransactionCategory'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='house',
            field=models.ForeignKey(to='website.House'),
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
    ]
