from django.db import models
from ..teachers.models import Exam, Question
from ..users.models import User


class AnsweredExam(models.Model):
    exam = models.ForeignKey(
        Exam, related_name="answered_exams", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        User, related_name="user_answers_exams", on_delete=models.CASCADE
    )

    def is_marked(self):
        answers = self.exam_answers.all()
        for answer in answers:
            if answer.score is None:
                return False
        return True

    def __str__(self) -> str:
        return f"{self.student}"


class Answers(models.Model):
    answered_exam = models.ForeignKey(
        AnsweredExam, related_name="exam_answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    answer = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.answer}"


class MultipleChoiceQuestions(models.Model):
    question = models.ForeignKey(
        Question, related_name="mc_answers", on_delete=models.CASCADE
    )
    answer = models.TextField()
    score = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.question
