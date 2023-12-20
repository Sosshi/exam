import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from apps.users.models import User
from apps.teachers.models import Exam, Question, Option, Result, Students
from apps.students.models import AnsweredExam, Answers


@pytest.fixture
def user():
    return User.objects.create_user(
        username="teacher",
        email="teacher@gmail.com",
        password="testpassword",
        is_teacher=True,
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        email="student@gmail.com", password="regularpassword", username="student"
    )


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def create_exam_url():
    return reverse("create_exam")


@pytest.fixture
def created_exam(exam_data):
    return Exam.objects.create(**exam_data)


@pytest.fixture
def created_essay_exam(exam_essay_data):
    return Exam.objects.create(**exam_essay_data)


@pytest.fixture
def student_user():
    return User.objects.create_user(
        username="student",
        email="student@gmail.com",
        password="studentpassword",
    )


@pytest.fixture
def created_answered_exams(created_exam, student_user):
    answered_exam1 = AnsweredExam.objects.create(
        exam=created_exam, student=student_user
    )
    answered_exam2 = AnsweredExam.objects.create(
        exam=created_exam, student=student_user
    )
    return answered_exam1, answered_exam2


@pytest.fixture
def created_question(created_exam):
    return Question.objects.create(
        question="What is math?", exam=created_exam, marks=56
    )


@pytest.fixture
def client_logged_as_teacher(teacher_user):
    client = Client()
    client.login(email="teacher@gmail.com", password="teacherpassword")
    return client


@pytest.fixture
def exam_data(teacher_user):
    return {
        "name": "Math Exam",
        "duration": 50,
        "start_datetime": timezone.now(),
        "exam_type": "mc",
        "pass_code": "pass_code",
        "teacher": teacher_user,
    }


@pytest.fixture
def exam_essay_data(teacher_user):
    return {
        "name": "Math Exam",
        "duration": 50,
        "start_datetime": timezone.now(),
        "exam_type": "essay",
        "pass_code": "pass_code",
        "teacher": teacher_user,
    }


@pytest.fixture
def created_answered_exam(created_exam, student_user):
    return AnsweredExam.objects.create(exam=created_exam, student=student_user)


@pytest.fixture
def created_answers(created_answered_exam, created_question):
    answer1 = Answers.objects.create(
        answered_exam=created_answered_exam,
        question=created_question,
        score=12,
        answer="test",
    )
    answer2 = Answers.objects.create(
        answered_exam=created_answered_exam,
        question=created_question,
        score=23,
        answer="test2",
    )
    return answer1, answer2


@pytest.fixture
def teacher_user():
    return User.objects.create_user(
        username="teacher",
        email="teacher@gmail.com",
        password="teacherpassword",
        is_teacher=True,
    )


@pytest.fixture
def created_exam(teacher_user):
    exam = Exam.objects.create(
        teacher=teacher_user,
        name="Test Exam",
        duration=60,
        start_datetime=timezone.now(),
        pass_code="test123",
        exam_type="essay",
    )
    return exam


@pytest.fixture
def created_option1(created_question):
    return Option.objects.create(question=created_question, name="3", is_answer=False)


@pytest.fixture
def created_option2(created_question):
    return Option.objects.create(question=created_question, name="4", is_answer=True)


@pytest.fixture
def created_option3(created_question):
    return Option.objects.create(question=created_question, name="5", is_answer=False)


@pytest.fixture
def created_result(created_exam):
    student = User.objects.create(
        username="student", email="student@example.com", password="studentpass"
    )
    return Result.objects.create(student=student, exam=created_exam, total_marks=5)


@pytest.fixture
def created_student_entry(created_exam):
    return Students.objects.create(exam=created_exam, student="student@example.com")
