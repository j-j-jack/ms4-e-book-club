# Generated by Django 3.2.9 on 2021-12-15 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20211215_1350'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookofmonth',
            old_name='Category',
            new_name='category',
        ),
    ]
