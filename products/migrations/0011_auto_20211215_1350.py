# Generated by Django 3.2.9 on 2021-12-15 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_alter_category_book_of_month'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='book_of_month',
        ),
        migrations.CreateModel(
            name='BookOfMonth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='book_of_month', to='products.category')),
                ('book_of_month', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='book_of_month', to='products.product')),
            ],
        ),
    ]
