# Generated by Django 3.2.9 on 2021-12-15 09:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0002_alter_review_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='review_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to=settings.AUTH_USER_MODEL),
        ),
    ]
