from allauth.account.forms import LoginForm, SignupForm
from .models import User
from django import forms


class TeacherSignUpForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        user.is_teacher = True
        user.save()
        return user


class UserCreationForm(SignupForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg text-4",
                "placeholder": "Enter your password",
                "required": True,
            }
        ),
    )
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg text-4",
                "placeholder": "Enter your email",
                "required": True,
            }
        ),
    )


class UserLoginForm(LoginForm):
    login = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg text-4",
                "placeholder": "Enter your email",
                "required": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg text-4",
                "placeholder": "Enter your password",
                "required": True,
            }
        ),
    )
