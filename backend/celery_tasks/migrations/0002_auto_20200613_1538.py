# Generated by Django 3.0.3 on 2020-06-13 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('celery_tasks', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Task',
            new_name='TaskScript',
        ),
    ]
