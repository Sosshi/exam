from django.urls import path
from .views import (
    StudentView,
    already_submitted,
    submit_uncompleted_essay,
    join_exam,
    write_essay,
    write_mc,
    submit_mc,
    SubmittedSuccessfully,
    submit_essay,
)

urlpatterns = [
    path("", StudentView.as_view(), name="student"),
    path("exam_essay/<int:exam_id>/", write_essay, name="write_essay"),
    path("exam_mc/<int:exam_id>/", write_mc, name="write_mc"),
    path("submit_mc/<int:exam_id>/", submit_mc, name="submit_mc"),
    path("success/", SubmittedSuccessfully.as_view(), name="success"),
    path("submit_essay/<int:exam_id>/", submit_essay, name="submit_essay"),
    path("join/", join_exam, name="join_exam"),
    path(
        "essay_uncomplete/<int:exam_id>/",
        submit_uncompleted_essay,
        name="essay_uncomplete",
    ),
    path("already_submitted", already_submitted, name="already_submitted"),
]
