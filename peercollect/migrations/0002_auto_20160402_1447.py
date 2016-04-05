# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peercollect', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peering',
            name='router',
            field=models.CharField(max_length=255, db_index=True),
        ),
    ]
