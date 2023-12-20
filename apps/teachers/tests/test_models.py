import pytest
from datetime import timedelta
from apps.teachers.models import Question


@pytest.mark.django_db
def test_exam_count_questions(created_exam):
    Question.objects.create(exam=created_exam, question="Question 1", marks=5)
    Question.objects.create(exam=created_exam, question="Question 2", marks=10)
    assert created_exam.count_questions() == 2


@pytest.mark.django_db
def test_exam_calculate_end_datetime(created_exam):
    end_datetime = created_exam.calculate_end_datetime()

    expected_end_datetime = created_exam.start_datetime + timedelta(
        minutes=created_exam.duration
    )
    assert end_datetime == expected_end_datetime


@pytest.mark.django_db
def test_exam_time_remaining(created_exam):
    remaining_time = created_exam.time_remaining()
    assert remaining_time >= 0


@pytest.mark.django_db
def test_exam_is_within_exam_time(created_exam):
    is_within_time = created_exam.is_within_exam_time()
    assert is_within_time


@pytest.mark.django_db
def test_exam_minutes_until_start(created_exam):
    minutes_until_start = created_exam.minutes_until_start()
    assert minutes_until_start >= 0


@pytest.mark.django_db
def test_question_str_method(created_question):
    assert str(created_question) == "What is math?"


@pytest.mark.django_db
def test_question_options_count(
    created_question, created_option1, created_option2, created_option3
):
    assert created_question.options.count() == 3


@pytest.mark.django_db
def test_question_correct_answer(
    created_question, created_option1, created_option2, created_option3
):
    correct_answer = created_question.options.get(is_answer=True)
    assert correct_answer.is_answer


@pytest.mark.django_db
def test_question_marks(created_question):
    assert created_question.marks == 56


@pytest.mark.django_db
def test_result_str_method(created_result):
    expected_result_str = f"{created_result.student.email} 500%"
    assert str(created_result) == expected_result_str


@pytest.mark.django_db
def test_result_marks_to_percent(created_result):
    assert created_result.marks_to_percent() == 500.0


@pytest.mark.django_db
def test_result_student(created_result):
    assert created_result.student == created_result.student


@pytest.mark.django_db
def test_result_exam(created_result):
    assert created_result.exam == created_result.exam


@pytest.mark.django_db
def test_result_total_marks(created_result):
    assert created_result.total_marks == 5


@pytest.mark.django_db
def test_students_str_method(created_student_entry):
    assert str(created_student_entry) == "Test Exam"


@pytest.mark.django_db
def test_students_exam(created_student_entry):
    assert created_student_entry.exam == created_student_entry.exam


@pytest.mark.django_db
def test_students_student_email(created_student_entry):
    assert created_student_entry.student == "student@example.com"


@pytest.mark.django_db
def test_option_str_method(created_option1):
    assert str(created_option1) == "3"


@pytest.mark.django_db
def test_option_question(created_option1):
    assert created_option1.question == created_option1.question


@pytest.mark.django_db
def test_option_is_answer(created_option1, created_option2, created_option3):
    assert not created_option1.is_answer
    assert created_option2.is_answer
    assert not created_option3.is_answer
