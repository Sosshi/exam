from django.contrib import admin
from .models import Option, Exam, Question, Result, Students


admin.site.register(Option)
admin.site.register(Question)
admin.site.register(Exam)
admin.site.register(Result)
admin.site.register(Students)