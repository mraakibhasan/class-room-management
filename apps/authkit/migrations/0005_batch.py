# Generated by Django 5.1.3 on 2024-12-03 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authkit', '0004_remove_user_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
