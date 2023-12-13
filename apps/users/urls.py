from django.urls import path
from .views import redirect_to_teacher_or_student, TeacherSignupView

urlpatterns = [
    path("", redirect_to_teacher_or_student, name="home"),
    path(
        "accounts/teacher_signup/", TeacherSignupView.as_view(), name="teacher_signup"
    ),
]
