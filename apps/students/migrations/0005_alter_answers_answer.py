# Generated by Django 5.0 on 2023-12-13 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_answers_answered_exam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answers',
            name='answer',
            field=models.TextField(blank=True, null=True),
        ),
    ]
