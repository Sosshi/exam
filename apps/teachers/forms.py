from django import forms
from .models import Question, Option, Exam, Students


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question", "marks"]


class McQuestionForm(forms.ModelForm):
    option = forms.CharField(max_length=200)

    class Meta:
        model = Question
        fields = ["question", "marks"]


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ["name"]


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "duration", "start_datetime", "exam_type", "pass_code"]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "duration": forms.TimeInput(attrs={"type": "time-local"}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ["student"]
