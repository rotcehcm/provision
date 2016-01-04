# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-30 17:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seguimiento', '0002_nuevapregunta_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='nuevapregunta',
            name='comentario',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='nuevapregunta',
            name='revisado',
            field=models.BooleanField(default=False),
        ),
    ]
