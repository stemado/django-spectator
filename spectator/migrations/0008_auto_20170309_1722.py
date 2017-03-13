# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spectator', '0007_auto_20170309_1715'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publicationseries',
            options={'ordering': ('sort_title',), 'verbose_name_plural': 'Publication series'},
        ),
        migrations.AddField(
            model_name='publicationseries',
            name='sort_title',
            field=models.CharField(blank=True, help_text="e.g. 'Alpine Review, The'. If left blank, will be created automatically on save.", max_length=255),
        ),
    ]