from django.test import TestCase
from apps.teachers.forms import QuestionForm, OptionForm, ExamForm, StudentForm
from apps.teachers.models import Question, Option, Exam, Students
from datetime import datetime, timedelta
from apps.users.models import User


class TestQuestionForm(TestCase):
    def test_question_form_valid(self):
        form_data = {"question": "Sample question?", "marks": 10}
        form = QuestionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_question_form_invalid(self):
        form_data = {"question": "", "marks": -5}  # Invalid data
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestOptionForm(TestCase):
    def test_option_form_valid(self):
        form_data = {"name": "Option A", "is_answer": True}
        form = OptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_option_form_invalid(self):
        form_data = {"name": "", "is_answer": False}  # Invalid data
        form = OptionForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestExamForm(TestCase):
    def test_exam_form_valid(self):
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
        self.assertTrue(form.is_valid())

    def test_exam_form_invalid(self):
        form_data = {
            "name": "",
            "duration": timedelta(hours=3),  # Invalid duration format
            "start_datetime": "invalid_date_format",  # Invalid datetime format
            "exam_type": "",
            "pass_code": "12",  # Invalid pass code length
        }
        form = ExamForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestStudentForm(TestCase):
    def test_student_form_valid(self):
        form_data = {"student": "student@gmail.com"}
        form = StudentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_student_form_invalid(self):
        form_data = {"student": ""}  # Invalid data
        form = StudentForm(data=form_data)
        self.assertFalse(form.is_valid())
