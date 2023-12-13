from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from apps.teachers.models import Exam, Question, Option
from apps.users.models import User
from apps.students.models import MultipleChoiceQuestions, Answers, AnsweredExam


class AnsweredExamModelTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create(
            email="teacher@example.com", password="teacherpass", username="teacher"
        )
        self.student_user = User.objects.create(
            email="student@example.com", password="studentpass", username="student"
        )
        self.exam = Exam.objects.create(
            teacher=self.teacher_user,
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="1234",
            exam_type="mc",
        )
        self.answered_exam = AnsweredExam.objects.create(
            exam=self.exam, student=self.student_user
        )

    def test_is_marked_false_when_unmarked_answers_exist(self):
        # Create unmarked answers for the answered exam
        question = Question.objects.create(
            exam=self.exam, question="Sample Question", marks=2
        )
        Answers.objects.create(
            answered_exam=self.answered_exam, question=question, answer="Sample Answer"
        )

        self.assertFalse(self.answered_exam.is_marked())

    def test_is_marked_true_when_all_answers_marked(self):
        # Create marked answers for the answered exam
        question1 = Question.objects.create(
            exam=self.exam, question="Sample Question 1", marks=2
        )
        question2 = Question.objects.create(
            exam=self.exam, question="Sample Question 2", marks=3
        )
        Answers.objects.create(
            answered_exam=self.answered_exam,
            question=question1,
            answer="Sample Answer 1",
            score=1.5,
        )
        Answers.objects.create(
            answered_exam=self.answered_exam,
            question=question2,
            answer="Sample Answer 2",
            score=2.5,
        )

        self.assertTrue(self.answered_exam.is_marked())


class MultipleChoiceQuestionsModelTest(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create(
            teacher=User.objects.create(
                email="teacher@example.com", password="teacherpass"
            ),
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="1234",
            exam_type="mc",
        )
        self.question = Question.objects.create(
            exam=self.exam, question="Sample MCQ", marks=2
        )
        self.mcq = MultipleChoiceQuestions.objects.create(
            question=self.question, answer="Option A", score=1.5
        )

    def test_mcq_str_representation(self):
        self.assertEqual(str(self.mcq.question), "Sample MCQ")


class AnswersModelTest(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create(
            teacher=User.objects.create(
                email="teacher@example.com", password="teacherpass", username="teacher"
            ),
            name="Sample Exam",
            duration=60,
            start_datetime=timezone.now(),
            slug="sample-exam",
            pass_code="1234",
            exam_type="mc",
        )
        self.answered_exam = AnsweredExam.objects.create(
            exam=self.exam,
            student=User.objects.create(
                email="student@example.com", password="studentpass", username="student"
            ),
        )
        self.question = Question.objects.create(
            exam=self.exam, question="Sample Question", marks=2
        )
        self.answer = Answers.objects.create(
            answered_exam=self.answered_exam,
            question=self.question,
            answer="Sample Answer",
            score=1.5,
        )

    def test_answer_str_representation(self):
        self.assertEqual(str(self.answer), "Sample Answer")
