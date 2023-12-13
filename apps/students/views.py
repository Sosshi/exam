from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


from ..teachers.models import Exam, Question, Option, Result, Students

from .models import Answers, AnsweredExam


class StudentView(LoginRequiredMixin, TemplateView):
    template_name = "students/student.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = Students.objects.all()
        exam = []
        for student in students:
            if student.student == self.request.user.email:
                exam.append(student.exam)
        context["exams"] = [i for i in set(exam)]
        return context


@login_required
def write_essay(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.all()
    if exam.is_within_exam_time():
        return render(
            request, "students/write_essay.html", {"exam": exam, "questions": questions}
        )
    if exam.calculate_end_datetime() < timezone.now():
        return render(request, "students/time_check_late.html")
    minutes_until_start = exam.minutes_until_start()
    remaining_time_str = format_remaining_time(minutes_until_start)

    return render(
        request, "students/time_check.html", {"remaining_time_str": remaining_time_str}
    )


@login_required
def write_mc(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.all()

    if exam.is_within_exam_time():
        return render(
            request, "students/write_mc.html", {"exam": exam, "questions": questions}
        )

    minutes_until_start = exam.minutes_until_start()
    remaining_time_str = format_remaining_time(minutes_until_start)

    return render(
        request, "students/time_check.html", {"remaining_time_str": remaining_time_str}
    )


def format_remaining_time(minutes):
    if minutes <= 0:
        return "Exam has already started"

    days, hours = divmod(minutes, 1440)
    hours, mins = divmod(hours, 60)
    remaining_time_str = f"{days} days, {hours} hours, {mins} minutes"

    return remaining_time_str


@require_POST
@login_required
def submit_mc(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == "POST":
        total_correct_answers = 0
        questions = Question.objects.filter(exam=exam)
        for question in questions:
            submitted_option_id = request.POST.get(f"question_{question.id}")
            correct_option = Option.objects.get(question=question, is_answer=True)
            if str(submitted_option_id) == str(correct_option.id):
                total_correct_answers += 1
        percentage_correct = total_correct_answers / questions.count()

        result = Result(
            student=request.user,
            exam=exam,
            total_marks=percentage_correct,
        )
        result.save()

        return redirect("success")
    else:
        pass
    return HttpResponse(405)


@require_POST
@login_required
def submit_essay(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    answered_exam = AnsweredExam.objects.create(exam=exam, student=request.user)
    questions = Question.objects.filter(exam=exam)
    try:
        for question in questions:
            question_answer = request.POST.get(f"question_{question.id}")
            answer = Answers(
                question=question, answer=question_answer, answered_exam=answered_exam
            )
            answer.save()
        return redirect("success")
    except Exception as e:
        return redirect("failed")


@login_required
def submit_uncompleted_essay(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = Question.objects.filter(exam=exam)
    answered_exam = AnsweredExam.objects.get(exam=exam, student=request.user)
    if not answered_exam:
        answered_exam = AnsweredExam.objects.create(exam=exam, student=request.user)
    else:
        prev_answers = Answers.objects.filter(answered_exam=answered_exam)
        for i in prev_answers:
            i.delete()
    for question in questions:
        question_answer = request.POST.get(f"question_{question.id}")
        print(question_answer)
        answer = Answers(
            question=question, answer=question_answer, answered_exam=answered_exam
        )
        answer.save()
        return HttpResponse(200)


class SubmittedSuccessfully(LoginRequiredMixin, TemplateView):
    template_name = "students/success.html"


@require_POST
@login_required
def join_exam(request):
    exam_pass_code = request.POST.get("pass_code")
    exam_id = request.POST.get("exam_id")
    exam = get_object_or_404(Exam, pk=int(exam_id))
    exams = Exam.objects.all()
    if request.POST:
        for exam in exams:
            if exam.pass_code == exam_pass_code and exam.pk == int(exam_id):
                student = Students(exam=exam, student=request.user.email)
                student.save()
                messages.success(request, f"You now have access to {student.exam.name}")
                return redirect("student")
    messages.error(request, "Request failed, check the pass code if it is correct")
    return redirect("student")


@login_required
def already_submitted(request):
    return render(request, "students/Already_submitted.html")
