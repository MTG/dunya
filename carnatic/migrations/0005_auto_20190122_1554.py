# Generated by Django 2.1.2 on 2019-01-22 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carnatic', '0004_auto_20161006_1700'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artist',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='concert',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='instrument',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='raaga',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='recording',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='taala',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='work',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='artist',
            name='artist_type',
            field=models.CharField(choices=[('P', 'Person'), ('G', 'Group')], default='P', max_length=1),
        ),
        migrations.AlterField(
            model_name='artist',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='composer',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True),
        ),
    ]
