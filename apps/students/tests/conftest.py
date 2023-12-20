import pytest
from django.utils import timezone
from apps.teachers.models import Exam, Question, Option, Students
from apps.users.models import User
from apps.students.models import Answers, AnsweredExam
from django.test import Client
from django.utils import timezone
from apps.students.models import AnsweredExam, Answers
from apps.users.models import User



@pytest.fixture
def teacher_user():
    return User.objects.create(
        email="teacher@example.com", password="teacherpass", username="teacher", is_teacher=True
    )


@pytest.fixture
def student_user():
    return User.objects.create(
        email="student@example.com", password="studentpass", username="student"
    )

@pytest.fixture
def client(student_user):
    client = Client()
    client.force_login(student_user)
    return client

@pytest.fixture
def exam(teacher_user):
    return Exam.objects.create(
        teacher=teacher_user,
        name="Sample Exam",
        duration=60,
        start_datetime=timezone.now(),
        slug="sample-exam",
        pass_code="1234",
        exam_type="mc",
    )
    
@pytest.fixture
def exam_access(teacher_user, student_user):
    exam = Exam.objects.create(
        teacher=teacher_user,
        name="Sample Exam",
        duration=60,
        start_datetime=timezone.now(),
        slug="sample-exam",
        pass_code="1234",
        exam_type="mc",
    )
    student = Students(exam=exam, student=student_user.email)
    student.save()
    return exam


@pytest.fixture
def answered_exam(exam, student_user):
    return AnsweredExam.objects.create(exam=exam, student=student_user)


@pytest.fixture
def question_essay(exam):
    return Question.objects.create(exam=exam, question="Sample Question", marks=2)


@pytest.fixture
def mcq(question_mc):
    return Question.objects.create(question=question_mc, answer="Option A", score=1.5)


@pytest.fixture
def answer(answered_exam, question_essay):
    return Answers.objects.create(
        answered_exam=answered_exam,
        question=question_essay,
        answer="Sample Answer",
        score=1.5,
    )


@pytest.fixture
def question_mc(exam):
    return Question.objects.create(exam=exam, question="Sample MCQ", marks=5)

@pytest.fixture
def option(question):
    return Option.objects.create(question=question, name="Option 1", is_answer=True)
