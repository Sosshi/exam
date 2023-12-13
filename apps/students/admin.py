from django.contrib import admin

from .models import AnsweredExam, Answers

admin.site.register(AnsweredExam)
admin.site.register(Answers)
