import pytest
from django.urls import reverse
from django.utils import timezone
from apps.teachers.models import Exam, Students, Result, Question, Option
from apps.students.models import Answers


@pytest.mark.django_db
def test_teacher_view_redirects_for_non_teacher(client, regular_user):
    response = client.login(email="student@gmail.com", password="regularpassword")
    assert response is True
    response = client.get(reverse("teacher"))
    assert response.status_code == 302  # Redirect status code
    assert response.url == reverse("student")


@pytest.mark.django_db
def test_teacher_view_for_teacher_user(client, user):
    response = client.login(email="teacher@gmail.com", password="testpassword")
    assert response is True
    response = client.get(reverse("teacher"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_teacher_mixin_redirects_for_non_teacher(client, regular_user):
    response = client.login(email="student@gmail.com", password="regularpassword")
    assert response is True
    response = client.get(reverse("teacher"))
    assert response.status_code == 302  # Redirect status code
    assert response.url == reverse("student")


@pytest.mark.django_db
def test_teacher_mixin_allows_teacher_user(client, user):
    response = client.login(email="teacher@gmail.com", password="testpassword")
    assert response is True
    response = client.get(reverse("teacher"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_exam_creation(client, teacher_user, create_exam_url):
    client.login(email="teacher@gmail.com", password="teacherpassword")
    response = client.get(create_exam_url)

    assert response.status_code == 200

    exam_data = {
        "name": "Math Exam",
        "duration": 50,
        "start_datetime": timezone.now(),
        "exam_type": "mc",
        "pass_code": "pass_code",
    }

    response = client.post(create_exam_url, data=exam_data, follow=True)

    assert response.status_code == 200
    assert Exam.objects.filter(name=exam_data["name"]).exists()


@pytest.mark.django_db
def test_exam_creation_failure(client, teacher_user, create_exam_url):
    client.login(email="teacher@gmail.com", password="teacherpassword")
    response = client.get(create_exam_url)

    assert response.status_code == 200

    invalid_exam_data = {
        # Missing required fields intentionally
    }

    response = client.post(create_exam_url, data=invalid_exam_data, follow=True)

    assert response.status_code == 200
    assert not Exam.objects.filter(name="").exists()


@pytest.mark.django_db
def test_create_exam_view_get(client, teacher_user, create_exam_url):
    client.login(email="teacher@gmail.com", password="teacherpassword")
    response = client.get(create_exam_url)

    assert response.status_code == 200
    assert "teachers/create_exam.html" in [
        template.name for template in response.templates
    ]


@pytest.mark.django_db
def test_create_exam_view_post_success(client, teacher_user, create_exam_url):
    exams_count_before = Exam.objects.count()

    exam_data = {
        "name": "Math Exam",
        "duration": 50,
        "start_datetime": timezone.now(),
        "exam_type": "mc",
        "pass_code": "pass_code",
    }

    client.login(email="teacher@gmail.com", password="teacherpassword")
    response = client.post(create_exam_url, data=exam_data, follow=True)

    assert response.status_code == 200
    assert "teachers/create_exam.html" in [
        template.name for template in response.templates
    ]
    assert Exam.objects.count() == exams_count_before + 1

    new_exam = Exam.objects.last()
    assert new_exam.name == exam_data["name"]


@pytest.mark.django_db
def test_create_exam_view_post_failure(client, teacher_user, create_exam_url):
    exams_count_before = Exam.objects.count()

    invalid_exam_data = {
        # Missing required fields intentionally
    }

    client.login(email="teacher@gmail.com", password="teacherpassword")
    response = client.post(create_exam_url, data=invalid_exam_data, follow=True)

    assert response.status_code == 200
    assert "teachers/create_exam.html" in [
        template.name for template in response.templates
    ]
    assert Exam.objects.count() == exams_count_before


@pytest.mark.django_db
def test_essay_question_create_page_get(client_logged_as_teacher, created_essay_exam):
    url = reverse("create_essay_questions", args=[created_essay_exam.id])
    response = client_logged_as_teacher.get(url)

    assert response.status_code == 200
    assert "teachers/create_essay_questions.html" in [
        template.name for template in response.templates
    ]


@pytest.mark.django_db
def test_essay_question_create_page_post(client_logged_as_teacher, created_exam):
    url = reverse("create_essay_questions", args=[created_exam.id])
    questions_count_before = Question.objects.filter(exam=created_exam).count()

    question_data = {
        "question": "Example Question",
        "exam": created_exam.id,
        "marks": 30,
    }

    response = client_logged_as_teacher.post(url, data=question_data, follow=True)

    assert response.status_code == 200
    assert "teachers/create_essay_questions.html" in [
        template.name for template in response.templates
    ]
    assert (
        Question.objects.filter(exam=created_exam).count() == questions_count_before + 1
    )

    new_question = Question.objects.filter(exam=created_exam).last()
    assert new_question.question == "Example Question"


@pytest.mark.django_db
def test_essay_question_create_success(client_logged_as_teacher, created_exam):
    url = reverse("create_essay_questions_form", args=[created_exam.id])
    questions_count_before = Question.objects.filter(exam=created_exam).count()

    question_data = {
        "question": "Essay Question",
        "exam": created_exam.id,
        "marks": 34,
    }

    response = client_logged_as_teacher.post(url, data=question_data, follow=True)

    assert response.status_code == 200
    assert (
        Question.objects.filter(exam=created_exam).count() == questions_count_before + 1
    )

    new_question = Question.objects.filter(exam=created_exam).last()
    assert new_question.question == "Essay Question"


@pytest.mark.django_db
def test_essay_question_create_failure(client, created_exam):
    url = reverse("create_essay_questions_form", args=[created_exam.id])
    questions_count_before = Question.objects.filter(exam=created_exam).count()

    invalid_question_data = {
        # Missing required fields intentionally
    }

    response = client.post(url, data=invalid_question_data, follow=True)

    assert response.status_code == 200
    assert Question.objects.filter(exam=created_exam).count() == questions_count_before


@pytest.mark.django_db
def test_written_scripts(
    client_logged_as_teacher, created_exam, created_answered_exams
):
    url = reverse("scripts", args=[created_exam.id])

    response = client_logged_as_teacher.get(url)

    assert response.status_code == 200
    assert "teachers/mark.html" in [template.name for template in response.templates]
    assert list(response.context["answers"]) == list(created_answered_exams)


@pytest.mark.django_db
def test_written_script_mark(
    client_logged_as_teacher, created_answered_exam, created_answers
):
    url = reverse("written_script_mark", args=[created_answered_exam.id])
    response = client_logged_as_teacher.get(url)

    assert response.status_code == 200
    assert "teachers/mark_student.html" in [
        template.name for template in response.templates
    ]
    print(response.context["answers"])
    print(created_answers)
    assert list(response.context["answers"]) == list(created_answers)


@pytest.mark.django_db
def test_mark(client_logged_as_teacher, created_answered_exam, created_answers):
    answered_exam_id = created_answered_exam.id
    url = reverse("mark_script", args=[answered_exam_id])

    post_data = {
        f"comment_{created_answers[0].id}": "Good effort",
        f"marks{created_answers[0].id}": "80",
        f"comment_{created_answers[1].id}": "Could be improved",
        f"marks{created_answers[1].id}": "70",
    }

    response = client_logged_as_teacher.post(url, post_data, follow=True)

    assert response.status_code == 200

    updated_answer1 = Answers.objects.get(pk=created_answers[0].id)
    updated_answer2 = Answers.objects.get(pk=created_answers[1].id)

    assert updated_answer1.comment == "Good effort"
    assert updated_answer1.score == 80
    assert updated_answer2.comment == "Could be improved"
    assert updated_answer2.score == 70

    result = Result.objects.get(
        exam=created_answered_exam.exam, student=created_answered_exam.student
    )
    assert result.total_marks == 1.5


@pytest.mark.django_db
def test_delete_exam(client_logged_as_teacher, created_exam):
    exams_count_before = Exam.objects.count()

    url = reverse("delete_exam", args=[created_exam.id])
    response = client_logged_as_teacher.post(url, follow=True)

    assert response.status_code == 200
    assert Exam.objects.count() == exams_count_before - 1

    deleted_exam_exists = Exam.objects.filter(name="Math Exam").exists()
    assert not deleted_exam_exists


@pytest.mark.django_db
def test_add_option_to_question_success(client_logged_as_teacher, created_question):
    options_count_before = Option.objects.filter(question=created_question).count()
    option_data = {
        "name": "New Option",
    }

    url = reverse("add_option_to_question", args=[created_question.id])
    response = client_logged_as_teacher.post(url, data=option_data, follow=True)

    assert response.status_code == 200

    # Ensure a new option was created for the question
    assert (
        Option.objects.filter(question=created_question).count()
        == options_count_before + 1
    )

    new_option = Option.objects.filter(
        question=created_question, name="New Option"
    ).last()
    assert new_option.name == "New Option"
    assert not new_option.is_answer


@pytest.mark.django_db
def test_add_option_to_question_failure(client_logged_as_teacher, created_question):
    url = reverse("add_option_to_question", args=[created_question.id])
    options_count_before = Option.objects.filter(question=created_question).count()

    invalid_option_data = {
        # Missing required fields intentionally
    }

    response = client_logged_as_teacher.post(url, data=invalid_option_data, follow=True)

    assert response.status_code == 200
    assert (
        Option.objects.filter(question=created_question).count() == options_count_before
    )


@pytest.mark.django_db
def test_delete_option(client_logged_as_teacher, created_question):
    option = Option.objects.create(question=created_question, name="Example Option")
    options_count_before = Option.objects.filter(question=created_question).count()

    url = reverse("delete_option", args=[option.id])
    response = client_logged_as_teacher.post(url, follow=True)

    assert response.status_code == 200
    assert (
        Option.objects.filter(question=created_question).count()
        == options_count_before - 1
    )

    deleted_option_exists = Option.objects.filter(name="Example Option").exists()
    assert not deleted_option_exists


@pytest.mark.django_db
def test_students_create_view_get(client_logged_as_teacher, created_exam):
    url = reverse("students_create", args=[created_exam.id])
    response = client_logged_as_teacher.get(url)

    assert response.status_code == 200
    assert "teachers/register_student.html" in [
        template.name for template in response.templates
    ]


@pytest.mark.django_db
def test_students_create_view_post(client_logged_as_teacher, created_exam):
    url = reverse("students_create", args=[created_exam.id])
    students_count_before = Students.objects.filter(exam=created_exam).count()

    student_data = {"student": "student@gmail.com", "exam": created_exam.id}

    response = client_logged_as_teacher.post(url, data=student_data, follow=True)

    assert response.status_code == 200
    assert (
        Students.objects.filter(exam=created_exam).count() == students_count_before + 1
    )

    new_student = Students.objects.filter(exam=created_exam).last()
    assert new_student.student == student_data["student"]


@pytest.mark.django_db
def test_students_create_success(client_logged_as_teacher, created_exam):
    url = reverse("students_create", args=[created_exam.id])
    students_count_before = Students.objects.filter(exam=created_exam).count()

    student_data = {"student": "student@gmail.com", "exam": created_exam.id}
    response = client_logged_as_teacher.post(url, data=student_data, follow=True)

    assert response.status_code == 200
    assert (
        Students.objects.filter(exam=created_exam).count() == students_count_before + 1
    )

    new_student = Students.objects.filter(exam=created_exam).last()
    assert new_student.student == student_data["student"]


@pytest.mark.django_db
def test_students_create_failure(client_logged_as_teacher, created_exam):
    url = reverse("students_create", args=[created_exam.id])
    students_count_before = Students.objects.filter(exam=created_exam).count()

    invalid_student_data = {}

    response = client_logged_as_teacher.post(
        url, data=invalid_student_data, follow=True
    )

    assert response.status_code == 200
    assert Students.objects.filter(exam=created_exam).count() == students_count_before
