# Generated by Django 5.0 on 2023-12-10 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answers',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='answers',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]