# Generated by Django 5.0 on 2023-12-11 12:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_multiplechoicequestions'),
    ]

    operations = [
        migrations.AddField(
            model_name='answers',
            name='answered_exam',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='exam_answers', to='students.answeredexam'),
            preserve_default=False,
        ),
    ]