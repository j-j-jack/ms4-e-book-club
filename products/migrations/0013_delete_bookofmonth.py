# Generated by Django 3.2.9 on 2021-12-15 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_rename_category_bookofmonth_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BookOfMonth',
        ),
    ]
