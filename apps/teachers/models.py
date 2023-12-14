from django.db import models
from django.utils.text import slugify
from datetime import timedelta, datetime
from django.utils import timezone
from ..users.models import User


class Exam(models.Model):
    teacher = models.ForeignKey(User, related_name="exams", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    duration = models.IntegerField()
    created_on = models.DateTimeField(auto_now=True)
    start_datetime = models.DateTimeField()
    slug = models.SlugField()
    pass_code = models.CharField(max_length=100)
    exam_type = models.CharField(
        max_length=20, choices=(("mc", "multiple choice"), ("essay", "Open Questions"))
    )

    def count_questions(self):
        return self.questions.count()

    def results_count(self):
        return self.results.count()

    def calculate_end_datetime(self):
        duration_in_minutes = self.duration
        start_datetime = self.start_datetime
        end_datetime = start_datetime + timedelta(minutes=duration_in_minutes)
        return end_datetime

    def time_remaining(self):
        current_time = timezone.now()
        end_datetime = self.calculate_end_datetime()

        if current_time < end_datetime:
            remaining_time = end_datetime - current_time
            remaining_minutes = remaining_time.total_seconds() // 60
            return remaining_minutes
        else:
            return 0

    def is_within_exam_time(self):
        current_time = timezone.now()
        start_time = self.start_datetime
        end_time = self.calculate_end_datetime()

        if start_time <= current_time <= end_time:
            return True
        else:
            return False

    def minutes_until_start(self):
        current_time = timezone.now()
        start_time = self.start_datetime

        if current_time < start_time:
            time_until_start = start_time - current_time
            minutes_until_start = time_until_start.total_seconds() // 60
            return minutes_until_start
        else:
            return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField()
    marks = models.FloatField()

    def __str__(self) -> str:
        return self.question


class Option(models.Model):
    question = models.ForeignKey(
        Question, related_name="options", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    is_answer = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Result(models.Model):
    student = models.ForeignKey(
        User, related_name="student_results", on_delete=models.CASCADE
    )
    exam = models.ForeignKey(Exam, related_name="results", on_delete=models.CASCADE)
    total_marks = models.FloatField()

    def marks_to_percent(self):
        return self.total_marks * 100

    def __str__(self) -> str:
        return f"{self.student.email} {self.marks_to_percent()}%"


class Students(models.Model):
    exam = models.ForeignKey(Exam, related_name="students", on_delete=models.CASCADE)
    student = models.EmailField()

    def __str__(self) -> str:
        return self.exam.name
