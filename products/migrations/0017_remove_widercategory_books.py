# Generated by Django 3.2.9 on 2021-12-15 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_category_wider_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='widercategory',
            name='books',
        ),
    ]