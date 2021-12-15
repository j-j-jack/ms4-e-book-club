# Generated by Django 3.2.9 on 2021-12-15 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20211214_2111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='books',
        ),
        migrations.RemoveField(
            model_name='product',
            name='book_of_month',
        ),
        migrations.AddField(
            model_name='category',
            name='book_of_month',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='book_of_month', to='products.product'),
        ),
    ]
