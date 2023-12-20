import pytest
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from apps.teachers.forms import QuestionForm, OptionForm, ExamForm, StudentForm
from apps.users.models import User


@pytest.mark.django_db
def test_question_form_valid():
    form_data = {"question": "Sample question?", "marks": 10}
    form = QuestionForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_question_form_invalid():
    form_data = {"question": "", "marks": -5}  # Invalid data
    form = QuestionForm(data=form_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_option_form_valid():
    form_data = {"name": "Option A", "is_answer": True}
    form = OptionForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_option_form_invalid():
    form_data = {"name": "", "is_answer": False}  # Invalid data
    form = OptionForm(data=form_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_exam_form_valid():
    teacher = User.objects.create(
        username="teacher", email="teacher@example.com", password="jekrferfu3"
    )
    form_data = {
        "teacher": teacher,
        "name": "Sample Exam",
        "duration": 76,
        "start_datetime": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "exam_type": "mc",
        "pass_code": "1234",
    }
    form = ExamForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_exam_form_invalid():
    form_data = {
        "name": "",
        "duration": timedelta(hours=3),  # Invalid duration format
        "start_datetime": "invalid_date_format",  # Invalid datetime format
        "exam_type": "",
        "pass_code": "12",  # Invalid pass code length
    }
    form = ExamForm(data=form_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_student_form_valid():
    form_data = {"student": "student@gmail.com"}
    form = StudentForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_student_form_invalid():
    form_data = {"student": ""}  # Invalid data
    form = StudentForm(data=form_data)
    assert not form.is_valid()
