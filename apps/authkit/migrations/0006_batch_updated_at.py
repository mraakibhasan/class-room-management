# Generated by Django 5.1.3 on 2024-12-03 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authkit', '0005_batch'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
