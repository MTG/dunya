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
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_id', models.IntegerField()),
                ('entity_type', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='UserFollowsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(verbose_name=b'date follow')),
                ('user_followed', models.ForeignKey(related_name='to_follow_set', to=settings.AUTH_USER_MODEL)),
                ('user_follower', models.ForeignKey(related_name='follow_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('birthday', models.DateField(null=True, blank=True)),
                ('avatar', models.ImageField(upload_to=b'gallery', blank=True)),
                ('affiliation', models.CharField(max_length=200, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='annotation',
            name='tag',
            field=models.ForeignKey(to='social.Tag'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='userfollowsuser',
            unique_together=set([('user_follower', 'user_followed')]),
        ),
        migrations.AlterUniqueTogether(
            name='annotation',
            unique_together=set([('user', 'tag', 'entity_id', 'entity_type')]),
        ),
    ]
