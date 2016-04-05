# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_peeringdb', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Peering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('router', models.CharField(max_length=255)),
                ('netixlan', models.OneToOneField(to='django_peeringdb.NetworkIXLan')),
            ],
        ),
    ]
