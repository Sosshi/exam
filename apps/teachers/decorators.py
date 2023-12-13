from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_teacher:
            messages.error(request, "You are not authorized to access this page.")
            return redirect("student")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
