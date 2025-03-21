# Generated by Django 5.1.5 on 2025-03-19 19:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_medications_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='booking',
        ),
        migrations.AddField(
            model_name='prescription',
            name='doctor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.doctor'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pres_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
