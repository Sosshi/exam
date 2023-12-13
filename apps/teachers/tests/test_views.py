from django.test import TestCase
from django.urls import reverse
from apps.users.models import User
from django.test.client import Client
from django.utils import timezone

from apps.teachers.models import Exam, Result, Students, Question, Option
from apps.students.models import AnsweredExam, Answers
from apps.teachers.views import ExamCreateView


class TeacherViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="testpassword",
            is_teacher=True,
        )
        self.client = Client()

    def test_teacher_view_redirects_for_non_teacher(self):
        regular_user = User.objects.create_user(
            email="student@gmail.com", password="regularpassword", username="student"
        )
        self.client.login(email="student@gmail.com", password="regularpassword")
        response = self.client.get(reverse("teacher"))
        self.assertRedirects(response, reverse("student"))

    def test_teacher_view_for_teacher_user(self):
        self.client.login(
            password="testpassword",
            email="teacher@gmail.com",
        )
        response = self.client.get(reverse("teacher"))
        self.assertEqual(response.status_code, 200)

    def test_teacher_mixin_redirects_for_non_teacher(self):
        regular_user = User.objects.create_user(
            email="student@gmail.com", password="regularpassword", username="student"
        )
        self.client.login(email="student@gmail.com", password="regularpassword")
        response = self.client.get(reverse("teacher"))
        self.assertRedirects(response, reverse("student"))

    def test_teacher_mixin_allows_teacher_user(self):
        self.client.login(
            password="testpassword",
            email="teacher@gmail.com",
        )
        response = self.client.get(reverse("teacher"))
        self.assertEqual(response.status_code, 200)


class ExamCreateViewTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.create_exam_url = reverse("create_exam")

    def test_exam_creation(self):
        self.client.login(email="teacher@gmail.com", password="teacherpassword")
        response = self.client.get(self.create_exam_url)

        self.assertEqual(response.status_code, 200)

        exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        response = self.client.post(self.create_exam_url, data=exam_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Exam.objects.filter(name=exam_data["name"]).exists())

    def test_exam_creation_failure(self):
        self.client.login(email="teacher@gmail.com", password="teacherpassword")
        response = self.client.get(self.create_exam_url)

        self.assertEqual(response.status_code, 200)

        invalid_exam_data = {
            # Missing required fields intentionally
        }

        response = self.client.post(
            self.create_exam_url, data=invalid_exam_data, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Exam.objects.filter(name="").exists())


class CreateExamViewTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

    def test_create_exam_view_get(self):
        response = self.client.get(reverse("create_exam"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/create_exam.html")

    def test_create_exam_view_post_success(self):
        exams_count_before = Exam.objects.count()

        exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        response = self.client.post(reverse("create_exam"), data=exam_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/create_exam.html")
        self.assertEqual(Exam.objects.count(), exams_count_before + 1)

        new_exam = Exam.objects.last()
        self.assertEqual(new_exam.name, exam_data["name"])

    def test_create_exam_view_post_failure(self):
        exams_count_before = Exam.objects.count()

        invalid_exam_data = {
            # Missing required fields intentionally
        }

        response = self.client.post(
            reverse("create_exam"), data=invalid_exam_data, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/create_exam.html")
        self.assertEqual(Exam.objects.count(), exams_count_before)


class EssayQuestionCreatePageTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

    def test_essay_question_create_page_get(self):
        url = reverse("create_essay_questions", args=[self.exam.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/create_essay_questions.html")

    def test_essay_question_create_page_post(self):
        url = reverse("create_essay_questions", args=[self.exam.id])
        questions_count_before = Question.objects.filter(exam=self.exam).count()

        question_data = {"question": "Example Question", "exam": self.exam, "marks": 30}

        response = self.client.post(url, data=question_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/create_essay_questions.html")
        self.assertEqual(
            Question.objects.filter(exam=self.exam).count(), questions_count_before + 1
        )

        new_question = Question.objects.filter(exam=self.exam).last()
        self.assertEqual(new_question.question, "Example Question")


class EssayQuestionCreateTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

    def test_essay_question_create_success(self):
        url = reverse("create_essay_questions_form", args=[self.exam.id])
        questions_count_before = Question.objects.filter(exam=self.exam).count()

        question_data = {
            "question": "Essay Question",
            "exam": self.exam,
            "marks": 34,
        }

        response = self.client.post(url, data=question_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Question.objects.filter(exam=self.exam).count(), questions_count_before + 1
        )

        new_question = Question.objects.filter(exam=self.exam).last()
        self.assertEqual(new_question.question, "Essay Question")

    def test_essay_question_create_failure(self):
        url = reverse("create_essay_questions_form", args=[self.exam.id])
        questions_count_before = Question.objects.filter(exam=self.exam).count()

        invalid_question_data = {
            # Missing required fields intentionally
        }

        response = self.client.post(url, data=invalid_question_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Question.objects.filter(exam=self.exam).count(), questions_count_before
        )


class WrittenScriptsTest(TestCase):
    def setUp(self):
        # Create a user to simulate as a teacher
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@gmail.com",
            password="teacherpassword",
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")
        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

        self.answered_exam1 = AnsweredExam.objects.create(
            exam=self.exam, student=self.student
        )
        self.answered_exam2 = AnsweredExam.objects.create(
            exam=self.exam, student=self.student
        )

    def test_written_scripts(self):
        url = reverse("scripts", args=[self.exam.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/mark.html")
        self.assertCountEqual(
            response.context["answers"],
            [self.answered_exam1, self.answered_exam2],
        )


class WrittenScriptMarkTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@gmail.com",
            password="studentpassword",
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )
        self.answered_exam = AnsweredExam.objects.create(
            exam=self.exam, student=self.student
        )
        self.question = Question.objects.create(
            question="What is math?", exam=self.exam, marks=56
        )

        self.answer1 = Answers.objects.create(
            answered_exam=self.answered_exam, question=self.question
        )
        self.answer2 = Answers.objects.create(
            answered_exam=self.answered_exam, question=self.question
        )

    def test_written_script_mark(self):
        url = reverse("written_script_mark", args=[self.answered_exam.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/mark_student.html")

        self.assertQuerysetEqual(
            list(response.context["answers"]),
            [self.answer1, self.answer2],
        )


class MarkTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@gmail.com",
            password="studentpassword",
        )
        self.answered_exam = AnsweredExam.objects.create(
            exam=self.exam, student=self.student
        )

        self.question = Question.objects.create(
            question="What is math?", exam=self.exam, marks=56
        )

        self.answer1 = Answers.objects.create(
            answered_exam=self.answered_exam, question=self.question, score=12
        )
        self.answer2 = Answers.objects.create(
            answered_exam=self.answered_exam, question=self.question, score=23
        )

    def test_mark(self):
        url = reverse("mark_script", args=[self.answered_exam.id])

        post_data = {
            f"comment_{self.answer1.id}": "Good effort",
            f"marks{self.answer1.id}": "80",
            f"comment_{self.answer2.id}": "Could be improved",
            f"marks{self.answer2.id}": "70",
        }

        response = self.client.post(url, post_data, follow=True)

        self.assertEqual(response.status_code, 200)

        updated_answer1 = Answers.objects.get(pk=self.answer1.id)
        updated_answer2 = Answers.objects.get(pk=self.answer2.id)

        self.assertEqual(updated_answer1.comment, "Good effort")
        self.assertEqual(updated_answer1.score, 80)
        self.assertEqual(updated_answer2.comment, "Could be improved")
        self.assertEqual(updated_answer2.score, 70)

        result = Result.objects.get(exam=self.exam, student=self.answered_exam.student)
        self.assertEqual(result.total_marks, 1.5)


class DeleteExamTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

    def test_delete_exam(self):
        exams_count_before = Exam.objects.count()

        url = reverse("delete_exam", args=[self.exam.id])
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Exam.objects.count(), exams_count_before - 1)

        deleted_exam_exists = Exam.objects.filter(name="Example Exam").exists()
        self.assertFalse(deleted_exam_exists)


class AddOptionToQuestionTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

        self.question = Question.objects.create(
            exam=self.exam, question="Example Question", marks=23
        )

    def test_add_option_to_question_success(self):
        options_count_before = Option.objects.filter(question=self.question).count()

        option_data = {"name": "New Option", "is_answer": True}

        url = reverse("add_option_to_question", args=[self.question.id])
        response = self.client.post(url, data=option_data, follow=True)

        self.assertEqual(response.status_code, 200)

        # Ensure a new option was created for the question
        self.assertEqual(
            Option.objects.filter(question=self.question).count(),
            options_count_before + 1,
        )

        new_option = Option.objects.filter(question=self.question).last()
        self.assertEqual(new_option.name, "New Option")
        self.assertTrue(new_option.is_answer)

    def test_add_option_to_question_failure(self):
        url = reverse("add_option_to_question", args=[self.question.id])
        options_count_before = Option.objects.filter(question=self.question).count()

        invalid_option_data = {
            # Missing required fields intentionally
        }

        response = self.client.post(url, data=invalid_option_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Option.objects.filter(question=self.question).count(), options_count_before
        )


class DeleteOptionTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

        self.question = Question.objects.create(
            exam=self.exam, question="Example Question", marks=23
        )
        self.option = Option.objects.create(
            question=self.question, name="Example Option"
        )

    def test_delete_option(self):
        options_count_before = Option.objects.filter(question=self.question).count()

        url = reverse("delete_option", args=[self.option.id])
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Option.objects.filter(question=self.question).count(),
            options_count_before - 1,
        )

        deleted_option_exists = Option.objects.filter(name="Example Option").exists()
        self.assertFalse(deleted_option_exists)


class StudentsCreateViewTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

    def test_students_create_view_get(self):
        url = reverse("students_create", args=[self.exam.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teachers/register_student.html")

    def test_students_create_view_post(self):
        url = reverse("students_create", args=[self.exam.id])
        students_count_before = Students.objects.filter(exam=self.exam).count()

        student_data = {"student": "student@gmail.com", "exam": self.exam}

        response = self.client.post(url, data=student_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Students.objects.filter(exam=self.exam).count(), students_count_before + 1
        )

        new_student = Students.objects.filter(exam=self.exam).last()
        self.assertEqual(new_student.student, student_data["student"])


class StudentsCreateTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@gmail.com",
            password="teacherpassword",
            is_teacher=True,
        )
        self.client = Client()
        self.client.login(email="teacher@gmail.com", password="teacherpassword")

        self.exam_data = {
            "name": "Math Exam",
            "duration": 50,
            "start_datetime": timezone.now(),
            "exam_type": "mc",
            "pass_code": "pass_code",
        }

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            name=self.exam_data["name"],
            duration=self.exam_data["duration"],
            start_datetime=self.exam_data["start_datetime"],
            exam_type=self.exam_data["exam_type"],
            pass_code=self.exam_data["pass_code"],
        )

    def test_students_create_success(self):
        url = reverse("students_create", args=[self.exam.id])
        students_count_before = Students.objects.filter(exam=self.exam).count()

        student_data = {"student": "student@gmail.com", "exam": self.exam}
        response = self.client.post(url, data=student_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Students.objects.filter(exam=self.exam).count(), students_count_before + 1
        )

        new_student = Students.objects.filter(exam=self.exam).last()
        self.assertEqual(new_student.student, student_data["student"])

    def test_students_create_failure(self):
        url = reverse("students_create", args=[self.exam.id])
        students_count_before = Students.objects.filter(exam=self.exam).count()

        invalid_student_data = {}

        response = self.client.post(url, data=invalid_student_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Students.objects.filter(exam=self.exam).count(), students_count_before
        )
