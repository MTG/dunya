# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='annotation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='annotation',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='userfollowsuser',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='userfollowsuser',
            name='user_followed',
        ),
        migrations.RemoveField(
            model_name='userfollowsuser',
            name='user_follower',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='avatar',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='birthday',
        ),
        migrations.DeleteModel(
            name='Annotation',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.DeleteModel(
            name='UserFollowsUser',
        ),
    ]
