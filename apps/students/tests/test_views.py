from django.test import TestCase, Client
from django.urls import reverse
from apps.teachers.models import Exam, Question, Option, Result, Students
from apps.users.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.template.loader import render_to_string

from apps.students.models import AnsweredExam, Answers
from apps.students.views import SubmittedSuccessfully


class StudentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.exam = Exam.objects.create(
            teacher=self.user,
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="123456",
            exam_type="mc",
        )
        self.student = Students.objects.create(exam=self.exam, student=self.user.email)

    def test_student_view(self):
        url = reverse("student")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/student.html")
        self.assertIn("exams", response.context)
        self.assertEqual(len(response.context["exams"]), 1)


class WriteEssayViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@gmail.com", password="12345"
        )
        self.client.login(username="testuser", password="12345")
        self.exam = Exam.objects.create(
            teacher=self.user,
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="123456",
            exam_type="essay",
        )
        self.student = Students.objects.create(exam=self.exam, student=self.user.email)
        self.question = Question.objects.create(
            exam=self.exam, question="Sample question", marks=5
        )

    def test_write_essay_view_within_exam_time(self):
        url = reverse("write_essay", args=[self.exam.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/write_essay.html")
        self.assertIn("exam", response.context)
        self.assertIn("questions", response.context)

    def test_write_essay_view_before_exam_start(self):
        self.exam.start_datetime = timezone.now() + timedelta(hours=1)
        self.exam.save()

        url = reverse("write_essay", args=[self.exam.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/time_check.html")
        self.assertIn("remaining_time_str", response.context)
        self.assertIn("minutes", response.context["remaining_time_str"])

    def test_write_essay_view_after_exam_end(self):
        self.exam.start_datetime = timezone.now() - timedelta(hours=3)
        self.exam.save()

        url = reverse("write_essay", args=[self.exam.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/time_check_late.html")


class WriteMCViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.exam = Exam.objects.create(
            teacher=self.user,
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="123456",
            exam_type="mc",
        )
        self.student = Students.objects.create(exam=self.exam, student=self.user.email)
        self.question = Question.objects.create(
            exam=self.exam, question="Sample MCQ", marks=5
        )
        self.option1 = Option.objects.create(
            question=self.question, name="Option 1", is_answer=True
        )
        self.option2 = Option.objects.create(
            question=self.question, name="Option 2", is_answer=False
        )
        self.option3 = Option.objects.create(
            question=self.question, name="Option 3", is_answer=False
        )
        self.option4 = Option.objects.create(
            question=self.question, name="Option 4", is_answer=False
        )

    def test_write_mc_view_within_exam_time(self):
        url = reverse("write_mc", args=[self.exam.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/write_mc.html")
        self.assertIn("exam", response.context)
        self.assertIn("questions", response.context)

    def test_write_mc_view_before_exam_start(self):
        # Changing the exam start time to be 1 hour in the future
        self.exam.start_datetime = timezone.now() + timedelta(hours=1)
        self.exam.save()

        url = reverse("write_mc", args=[self.exam.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/time_check.html")
        self.assertIn("remaining_time_str", response.context)
        self.assertIn("minutes", response.context["remaining_time_str"])

    def test_write_mc_view_after_exam_end(self):
        self.exam.start_datetime = timezone.now() + timedelta(hours=3)
        self.exam.save()

        url = reverse("write_mc", args=[self.exam.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/time_check.html")
        self.assertIn("remaining_time_str", response.context)


class SubmitMCViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.exam = Exam.objects.create(
            teacher=self.user,
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="123456",
            exam_type="mc",
        )
        self.question1 = Question.objects.create(
            exam=self.exam, question="Sample MCQ 1", marks=5
        )
        self.option1_1 = Option.objects.create(
            question=self.question1, name="Option 1", is_answer=True
        )
        self.option1_2 = Option.objects.create(
            question=self.question1, name="Option 2", is_answer=False
        )

        self.question2 = Question.objects.create(
            exam=self.exam, question="Sample MCQ 2", marks=5
        )
        self.option2_1 = Option.objects.create(
            question=self.question2, name="Option 1", is_answer=True
        )
        self.option2_2 = Option.objects.create(
            question=self.question2, name="Option 2", is_answer=False
        )

    def test_submit_mc_valid(self):
        url = reverse("submit_mc", args=[self.exam.id])
        response = self.client.post(
            url,
            {
                f"question_{self.question1.id}": self.option1_1.id,
                f"question_{self.question2.id}": self.option2_2.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Result.objects.count(), 1)
        saved_result = Result.objects.first()
        self.assertEqual(saved_result.student, self.user)
        self.assertEqual(saved_result.exam, self.exam)
        self.assertEqual(saved_result.total_marks, 0.5)

    def test_submit_mc_no_post_data(self):
        url = reverse("submit_mc", args=[self.exam.id])
        response = self.client.get(url)  # Sending a GET request instead of POST

        self.assertEqual(
            response.status_code, 405
        )  # Method Not Allowed for GET requests
        self.assertEqual(Result.objects.count(), 0)


class SubmitEssayViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.exam = Exam.objects.create(
            teacher=self.user,
            name="Sample Essay Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-essay-exam",
            pass_code="123456",
            exam_type="essay",
        )
        self.question1 = Question.objects.create(
            exam=self.exam, question="Sample Essay Q1", marks=10
        )
        self.question2 = Question.objects.create(
            exam=self.exam, question="Sample Essay Q2", marks=5
        )

    def test_submit_essay_valid(self):
        url = reverse("submit_essay", args=[self.exam.id])
        response = self.client.post(
            url,
            {
                f"question_{self.question1.id}": "This is an answer for Q1",
                f"question_{self.question2.id}": "This is an answer for Q2",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(AnsweredExam.objects.count(), 1)
        answered_exam = AnsweredExam.objects.first()
        self.assertEqual(answered_exam.student, self.user)
        self.assertEqual(answered_exam.exam, self.exam)

        self.assertEqual(Answers.objects.count(), 2)
        saved_answers = Answers.objects.filter(answered_exam=answered_exam)
        self.assertEqual(saved_answers.count(), 2)

    def test_submit_essay_no_post_data(self):
        url = reverse("submit_essay", args=[self.exam.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(AnsweredExam.objects.count(), 0)
        self.assertEqual(Answers.objects.count(), 0)


class SubmittedSuccessfullyViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_submitted_successfully_view(self):
        url = reverse("success")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/success.html")
        self.assertIsInstance(response.context["view"], SubmittedSuccessfully)
        expected_html = render_to_string("students/success.html", context={})
        self.assertHTMLEqual(response.content.decode("utf-8"), expected_html)


class JoinExamViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.exam = Exam.objects.create(
            teacher=self.user,
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="123456",
            exam_type="mc",
        )

    def test_join_exam_valid(self):
        url = reverse("join_exam")
        response = self.client.post(
            url, {"pass_code": self.exam.pass_code, "exam_id": self.exam.id}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Students.objects.count(), 1)
        student = Students.objects.first()
        self.assertEqual(student.student, self.user.email)
        self.assertEqual(student.exam, self.exam)

    def test_join_exam_invalid_pass_code(self):
        url = reverse("join_exam")
        response = self.client.post(
            url,
            {
                "pass_code": "invalid_code",
                "exam_id": self.exam.id,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Students.objects.count(), 0)

    def test_join_exam_invalid_exam_id(self):
        url = reverse("join_exam")
        response = self.client.post(
            url,
            {
                "pass_code": self.exam.pass_code,
                "exam_id": 999,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Students.objects.count(), 0)


class AlreadySubmittedViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_already_submitted_view(self):
        url = reverse("already_submitted")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/Already_submitted.html")
