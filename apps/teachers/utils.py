from django.core.mail import send_mass_mail
from .models import Exam, Students, Result

from apps.users.models import User


def send_result_emails(exam_id):
    exam = Exam.objects.get(pk=exam_id)
    students = Students.objects.all()
    email_list = []
    user = None
    result = None
    for student in students:
        user = User.objects.get(email=student.student)
        result = Result.objects.get(student=user)
        if user:
            email_list.append(
                (
                    f"Subject {result.exam}",
                    f"You scored {result.total_marks}",
                    f"{exam.teacher.email}",
                    [f"{student.student}"],
                )
            )

    messages = [
        (subject, message, from_email, to_email)
        for subject, message, from_email, to_email in email_list
    ]

    send_mass_mail(messages)
