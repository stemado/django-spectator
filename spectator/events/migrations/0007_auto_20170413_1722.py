# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-13 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20170413_1722'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='dance_pieces',
            new_name='dancepieces',
        ),
        migrations.AlterField(
            model_name='dancepiece',
            name='creators',
            field=models.ManyToManyField(related_name='dancepieces', through='events.DancePieceRole', to='core.Creator'),
        ),
    ]