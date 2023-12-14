from django.core.mail import send_mass_mail
from .models import Exam, Result


def send_result_emails(exam_id):
    exam = Exam.objects.get(pk=exam_id)
    results = Result.objects.filter(exam=exam)
    email_list = []
    for result in results:
        email_list.append(
            (
                f"Your results for exam {result.exam}",
                f"You scored {result.total_marks}",
                f"{result.exam.teacher.email}",
                [f"{result.student.email}"],
            )
        )

    messages = [
        (subject, message, from_email, to_email)
        for subject, message, from_email, to_email in email_list
    ]
    send_mass_mail(messages)
