# Generated by Django 5.0 on 2023-12-12 00:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0006_alter_exam_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='end_datetime',
        ),
    ]