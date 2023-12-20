import pytest
from apps.teachers.models import Question
from apps.students.models import Answers

@pytest.mark.django_db
def test_is_marked_false_when_unmarked_answers_exist(answered_exam, exam, question_essay):
    Answers.objects.create(
        answered_exam=answered_exam, question=question_essay, answer="Sample Answer"
    )
    assert not answered_exam.is_marked()

@pytest.mark.django_db
def test_is_marked_true_when_all_answers_marked(answered_exam, exam):
    question1 = Question.objects.create(exam=exam, question="Sample Question 1", marks=2)
    question2 = Question.objects.create(exam=exam, question="Sample Question 2", marks=3)
    Answers.objects.create(
        answered_exam=answered_exam,
        question=question1,
        answer="Sample Answer 1",
        score=1.5,
    )
    Answers.objects.create(
        answered_exam=answered_exam,
        question=question2,
        answer="Sample Answer 2",
        score=2.5,
    )

    assert answered_exam.is_marked()

@pytest.mark.django_db
def test_mcq_str_representation(question_mc):
    assert str(question_mc.question) == "Sample MCQ"

@pytest.mark.django_db
def test_answer_str_representation(answer):
    assert str(answer) == "Sample Answer"
