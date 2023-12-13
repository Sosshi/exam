from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin


class TeacherRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_teacher:
            messages.error(request, "You are not authorized to access this page.")
            return redirect(reverse("student"))
        return super().dispatch(request, *args, **kwargs)
