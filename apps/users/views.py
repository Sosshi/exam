from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from allauth.account.views import SignupView
from .forms import TeacherSignUpForm


@login_required()
def redirect_to_teacher_or_student(request):
    if request.user.is_teacher:
        return redirect(reverse("teacher"))
    return redirect(reverse("student"))


class TeacherSignupView(SignupView):
    form_class = TeacherSignUpForm
    template_name = "account/teacher_signup.html"
