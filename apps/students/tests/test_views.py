import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from django.utils import timezone
from apps.teachers.models import  Students, Result, Question, Option
from apps.students.models import AnsweredExam, Answers
from datetime import timedelta
from apps.students.views import SubmittedSuccessfully
from django.template.loader import render_to_string

@pytest.mark.django_db
def test_student_view(client, exam_access, student_user):
    url = reverse("student")
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "students/student.html")
    assert "exams" in response.context
    print(response.context)
    assert len(response.context["exams"]) == 1


@pytest.mark.django_db
def test_write_essay_view_within_exam_time(client, student_user, exam):
    url = reverse("write_essay", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "students/write_essay.html")
    assert "exam" in response.context
    assert "questions" in response.context

@pytest.mark.django_db
def test_write_essay_view_before_exam_start(client, student_user, exam):
    exam.start_datetime = timezone.now() + timedelta(hours=1)
    exam.save()

    url = reverse("write_essay", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "students/time_check.html")
    assert "remaining_time_str" in response.context
    assert "minutes" in response.context["remaining_time_str"]

@pytest.mark.django_db
def test_write_essay_view_after_exam_end(client, student_user, exam):
    exam.start_datetime = timezone.now() - timedelta(hours=3)
    exam.save()

    url = reverse("write_essay", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "students/time_check_late.html")


@pytest.mark.django_db
def test_write_mc_view_within_exam_time(client, student_user, exam, question_mc):
    Option.objects.create(question=question_mc, name="Option 1", is_answer=True)
    Option.objects.create(question=question_mc, name="Option 2", is_answer=False)
    Option.objects.create(question=question_mc, name="Option 3", is_answer=False)
    Option.objects.create(question=question_mc, name="Option 4", is_answer=False)

    url = reverse("write_mc", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "students/write_mc.html")
    assert "exam" in response.context
    assert "questions" in response.context

@pytest.mark.django_db
def test_write_mc_view_before_exam_start(client, student_user, exam):
    exam.start_datetime = timezone.now() + timedelta(hours=1)
    exam.save()

    url = reverse("write_mc", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "students/time_check.html")
    assert "remaining_time_str" in response.context
    assert "minutes" in response.context["remaining_time_str"]

@pytest.mark.django_db
def test_write_mc_view_after_exam_end(client, student_user, exam):
    exam.start_datetime = timezone.now() + timedelta(hours=3)
    exam.save()

    url = reverse("write_mc", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 200
    assertTemplateUsed(response, "students/time_check.html")
    assert "remaining_time_str" in response.context


@pytest.mark.django_db
def test_submit_mc_valid(client, student_user, exam):
    question1 = Question.objects.create(exam=exam, question="Sample MCQ 1", marks=5)
    option1_1 = Option.objects.create(question=question1, name="Option 1", is_answer=True)
    Option.objects.create(question=question1, name="Option 2", is_answer=False)

    question2 = Question.objects.create(exam=exam, question="Sample MCQ 2", marks=5)
    Option.objects.create(question=question2, name="Option 1", is_answer=True)
    option2_2 = Option.objects.create(question=question2, name="Option 2", is_answer=False)

    url = reverse("submit_mc", args=[exam.id])
    response = client.post(
        url,
        {
            f"question_{question1.id}": option1_1.id,
            f"question_{question2.id}": option2_2.id,
        },
    )

    assert response.status_code == 302
    assert Result.objects.count() == 1
    saved_result = Result.objects.first()
    assert saved_result.student == student_user
    assert saved_result.exam == exam
    assert saved_result.total_marks == 0.5

@pytest.mark.django_db
def test_submit_mc_no_post_data(client, student_user, exam):
    url = reverse("submit_mc", args=[exam.id])
    response = client.get(url)  # Sending a GET request instead of POST

    assert response.status_code == 405  # Method Not Allowed for GET requests
    assert Result.objects.count() == 0

@pytest.mark.django_db
def test_submit_essay_valid(client, student_user, exam):
    question1 = Question.objects.create(exam=exam, question="Sample Essay Q1", marks=10)
    question2 = Question.objects.create(exam=exam, question="Sample Essay Q2", marks=5)

    url = reverse("submit_essay", args=[exam.id])
    response = client.post(
        url,
        {
            f"question_{question1.id}": "This is an answer for Q1",
            f"question_{question2.id}": "This is an answer for Q2",
        },
    )

    assert response.status_code == 302
    assert AnsweredExam.objects.count() == 1
    answered_exam = AnsweredExam.objects.first()
    assert answered_exam.student == student_user
    assert answered_exam.exam == exam

    assert Answers.objects.count() == 2
    saved_answers = Answers.objects.filter(answered_exam=answered_exam)
    assert saved_answers.count() == 2

@pytest.mark.django_db
def test_submit_essay_no_post_data(client, student_user, exam):
    url = reverse("submit_essay", args=[exam.id])
    response = client.get(url)

    assert response.status_code == 405
    assert AnsweredExam.objects.count() == 0
    assert Answers.objects.count() == 0

@pytest.mark.django_db
def test_submitted_successfully_view(client, student_user):
    url = reverse("success")
    response = client.get(url)

    assert response.status_code == 200
    assert "students/success.html" in [template.name for template in response.templates]
    assert isinstance(response.context["view"], SubmittedSuccessfully)
    
    expected_html = render_to_string("students/success.html", context={})
    assert response.content.decode("utf-8") == expected_html

@pytest.mark.django_db
def test_join_exam_valid(client, student_user, exam):
    url = reverse("join_exam")
    response = client.post(url, {"pass_code": exam.pass_code, "exam_id": exam.id})

    assert response.status_code == 302
    assert Students.objects.count() == 1
    student = Students.objects.first()
    assert student.student == student_user.email
    assert student.exam == exam

@pytest.mark.django_db
def test_join_exam_invalid_pass_code(client, student_user, exam):
    url = reverse("join_exam")
    response = client.post(
        url,
        {
            "pass_code": "invalid_code",
            "exam_id": exam.id,
        },
    )

    assert response.status_code == 302
    assert Students.objects.count() == 0

@pytest.mark.django_db
def test_join_exam_invalid_exam_id(client, student_user, exam):
    url = reverse("join_exam")
    response = client.post(
        url,
        {
            "pass_code": exam.pass_code,
            "exam_id": 999,
        },
    )

    assert response.status_code == 404
    assert Students.objects.count() == 0

@pytest.mark.django_db
def test_already_submitted_view(client, student_user):
    url = reverse("already_submitted")
    response = client.get(url)

    assert response.status_code == 200
    assert "students/Already_submitted.html" in [template.name for template in response.templates]
