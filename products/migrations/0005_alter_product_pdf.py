# Generated by Django 3.2.9 on 2021-11-30 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='pdfs'),
        ),
    ]
