# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 09:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spectator', '0004_auto_20170301_0906'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True, help_text='The time this item was created in the database.')),
                ('time_modified', models.DateTimeField(auto_now=True, help_text='The time this item was last saved to the database.')),
                ('role_name', models.CharField(blank=True, help_text="e.g. 'Headliner', 'Support', 'Editor', 'Illustrator', 'Director', etc.", max_length=50)),
                ('role_order', models.PositiveSmallIntegerField(default=1, help_text='The order in which the Creators will be listed.')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spectator.Book')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spectator.Creator')),
            ],
            options={
                'ordering': ('role_order', 'role_name'),
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='role',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='role',
            name='creator',
        ),
        migrations.AlterModelOptions(
            name='reading',
            options={'ordering': ('end_date',)},
        ),
        migrations.DeleteModel(
            name='Role',
        ),
        migrations.AddField(
            model_name='book',
            name='creators',
            field=models.ManyToManyField(through='spectator.BookRole', to='spectator.Creator'),
        ),
    ]
