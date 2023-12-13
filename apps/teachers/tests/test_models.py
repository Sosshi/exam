from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.teachers.models import Exam, Question, Option, Result, Students


class ExamModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create(
            is_teacher=True, email="teacher@example.com", password="userpass"
        )

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name="Test Exam",
            duration=60,
            start_datetime=timezone.now(),
            pass_code="test123",
            exam_type="essay",
        )

    def test_exam_count_questions(self):
        Question.objects.create(exam=self.exam, question="Question 1", marks=5)
        Question.objects.create(exam=self.exam, question="Question 2", marks=10)
        self.assertEqual(self.exam.count_questions(), 2)

    def test_exam_calculate_end_datetime(self):
        end_datetime = self.exam.calculate_end_datetime()

        expected_end_datetime = self.exam.start_datetime + timedelta(
            minutes=self.exam.duration
        )
        self.assertEqual(end_datetime, expected_end_datetime)

    def test_exam_time_remaining(self):
        remaining_time = self.exam.time_remaining()
        self.assertGreaterEqual(remaining_time, 0)

    def test_exam_is_within_exam_time(self):
        is_within_time = self.exam.is_within_exam_time()
        self.assertTrue(is_within_time)

    def test_exam_minutes_until_start(self):
        minutes_until_start = self.exam.minutes_until_start()
        self.assertGreaterEqual(minutes_until_start, 0)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create(
            username="teacher", email="teacher@example.com"
        )

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name="Test Exam",
            duration=60,
            start_datetime=timezone.now(),
            pass_code="test123",
            exam_type="mc",
        )

        self.question = Question.objects.create(
            exam=self.exam, question="What is 2 + 2?", marks=5
        )

        self.option1 = Option.objects.create(
            question=self.question, name="3", is_answer=False
        )
        self.option2 = Option.objects.create(
            question=self.question, name="4", is_answer=True
        )
        self.option3 = Option.objects.create(
            question=self.question, name="5", is_answer=False
        )

    def test_question_str_method(self):
        self.assertEqual(str(self.question), "What is 2 + 2?")

    def test_question_options_count(self):
        self.assertEqual(self.question.options.count(), 3)

    def test_question_correct_answer(self):
        correct_answer = self.question.options.get(is_answer=True)

        self.assertTrue(correct_answer.is_answer)

    def test_question_marks(self):
        self.assertEqual(self.question.marks, 5)


class ResultModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create(
            username="student", email="student@example.com"
        )

        self.teacher = User.objects.create(
            username="teacher", email="teacher@example.com"
        )

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name="Test Exam",
            duration=60,
            start_datetime=timezone.now(),
            pass_code="test123",
            exam_type="mc",
        )

        self.question = Question.objects.create(
            exam=self.exam, question="What is 2 + 2?", marks=5
        )

        self.option1 = Option.objects.create(
            question=self.question, name="3", is_answer=False
        )
        self.option2 = Option.objects.create(
            question=self.question, name="4", is_answer=True
        )
        self.option3 = Option.objects.create(
            question=self.question, name="5", is_answer=False
        )

        self.result = Result.objects.create(
            student=self.student, exam=self.exam, total_marks=5
        )

    def test_result_str_method(self):
        expected_result_str = f"{self.student.email} 500%"
        self.assertEqual(str(self.result), expected_result_str)

    def test_result_marks_to_percent(self):
        self.assertEqual(self.result.marks_to_percent(), 500.0)

    def test_result_student(self):
        self.assertEqual(self.result.student, self.student)

    def test_result_exam(self):
        self.assertEqual(self.result.exam, self.exam)

    def test_result_total_marks(self):
        self.assertEqual(self.result.total_marks, 5)


class StudentsModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create(
            username="teacher", email="teacher@example.com"
        )

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name="Test Exam",
            duration=60,
            start_datetime=timezone.now(),
            pass_code="test123",
            exam_type="mc",
        )

        self.student_entry = Students.objects.create(
            exam=self.exam, student="student@example.com"
        )

    def test_students_str_method(self):
        self.assertEqual(str(self.student_entry), "Test Exam")

    def test_students_exam(self):
        self.assertEqual(self.student_entry.exam, self.exam)

    def test_students_student_email(self):
        self.assertEqual(self.student_entry.student, "student@example.com")


class OptionModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create(
            username="teacher", email="teacher@example.com"
        )
        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name="Test Exam",
            duration=60,
            start_datetime=timezone.now(),
            pass_code="test123",
            exam_type="mc",
        )

        self.question = Question.objects.create(
            exam=self.exam, question="What is 2 + 2?", marks=5
        )

        self.option1 = Option.objects.create(
            question=self.question, name="3", is_answer=False
        )
        self.option2 = Option.objects.create(
            question=self.question, name="4", is_answer=True
        )
        self.option3 = Option.objects.create(
            question=self.question, name="5", is_answer=False
        )

    def test_option_str_method(self):
        self.assertEqual(str(self.option1), "3")

    def test_option_question(self):
        self.assertEqual(self.option1.question, self.question)

    def test_option_is_answer(self):
        self.assertFalse(self.option1.is_answer)
        self.assertTrue(self.option2.is_answer)
        self.assertFalse(self.option3.is_answer)
