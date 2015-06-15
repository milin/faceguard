# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackListedWords',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeletedComments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('message_by', models.CharField(max_length=200)),
                ('message_id', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FacebookUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('access_token', models.TextField()),
                ('email_address', models.EmailField(max_length=50)),
                ('username', models.CharField(max_length=50)),
                ('blacklist_words', models.TextField(blank=True)),
                ('password', models.TextField(blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deletedcomments',
            name='user',
            field=models.ForeignKey(to='facebook.FacebookUser'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blacklistedwords',
            name='user',
            field=models.ForeignKey(to='facebook.FacebookUser'),
            preserve_default=True,
        ),
    ]
