# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-18 17:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seguimiento', '0011_auto_20160211_1015'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatoExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('dato', models.CharField(max_length=100)),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extras', to='seguimiento.NuevaPregunta')),
            ],
        ),
    ]
