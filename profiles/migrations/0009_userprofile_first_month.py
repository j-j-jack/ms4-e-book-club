# Generated by Django 3.2.9 on 2021-12-24 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0008_auto_20211224_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='first_month',
            field=models.BooleanField(default=False),
        ),
    ]
