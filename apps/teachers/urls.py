from django.urls import path

from .views import (
    TeacherView,
    students_create,
    delete_option,
    delete_exam,
    add_option_to_question,
    create_exam,
    essay_question_create,
    mark,
    essay_question_create_page,
    written_scripts,
    multiple_choice_quections,
    add_option_to_question,
    written_script_mark,
    delete_question,
    results_view,
    send_emails,
    delete_mc_question,
)

urlpatterns = [
    path("", TeacherView.as_view(), name="teacher"),
    path("create_exam/", create_exam, name="create_exam"),
    path(
        "create_essay_questions/<int:exam_id>/",
        essay_question_create_page,
        name="create_essay_questions",
    ),
    path(
        "create_essay/<int:exam_id>/",
        essay_question_create,
        name="create_essay_questions_form",
    ),
    path(
        "create_mc_questions/<int:exam_id>/",
        multiple_choice_quections,
        name="create_mc_questions",
    ),
    path(
        "create_option/<int:question_id>/",
        add_option_to_question,
        name="add_option_to_question",
    ),
    path("scripts/<int:exam_id>/", written_scripts, name="scripts"),
    path(
        "written_script_mark/<int:answered_exam_id>/",
        written_script_mark,
        name="written_script_mark",
    ),
    path("mark/<int:answer_exam_id>/", mark, name="mark_script"),
    path("delete/<int:exam_id>", delete_exam, name="delete_exam"),
    path("delete_question/<int:question_id>", delete_question, name="delete_question"),
    path(
        "delete_mc_question/<int:question_id>",
        delete_mc_question,
        name="delete_mc_question",
    ),
    path(
        "add_option_to_question/<int:question_id>/",
        add_option_to_question,
        name="add_option_to_question",
    ),
    path("delete_option/<int:option_id>/", delete_option, name="delete_option"),
    path("students/<int:exam_id>/", students_create, name="students_create"),
    path("results/<int:exam_id>/", results_view, name="results_view"),
    path("send_emails/<int:exam_id>/", send_emails, name="send_emails"),
]
