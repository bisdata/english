# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-05 10:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='coaching_details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=400)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=30)),
                ('pincode', models.PositiveIntegerField(max_length=6)),
                ('test', models.CharField(max_length=30)),
                ('batch_size', models.PositiveIntegerField(max_length=6)),
            ],
        ),
    ]
