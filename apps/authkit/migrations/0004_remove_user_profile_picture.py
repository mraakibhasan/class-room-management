# Generated by Django 5.1.3 on 2024-12-03 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authkit', '0003_alter_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_picture',
        ),
    ]
