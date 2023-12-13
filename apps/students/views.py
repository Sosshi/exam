from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from ..teachers.models import Exam, Question, Option, Result, Students

from .models import Answers, AnsweredExam


class StudentView(TemplateView):
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


@csrf_exempt
@require_POST
def save_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answer_text = request.POST.get("answer_text")

    answer, created = Answers.objects.get_or_create(question=question)
    answer.answer = answer_text
    answer.save()

    return JsonResponse({"status": "success"})


def submit_mc(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == "POST":
        total_marks = 0

        questions = Question.objects.filter(exam=exam)
        for question in questions:
            submitted_option_id = request.POST.get(f"question_{question.id}")
            print(f"question_{question.id}")
            print(submitted_option_id)
            correct_option = Option.objects.get(question=question, is_answer=True)
            print(correct_option)
            if str(submitted_option_id) == str(correct_option):
                total_marks += 1
        result = Result(
            student=request.user,
            exam=exam,
            total_marks=(total_marks / questions.count()),
        )
        result.save()
        return redirect("success")
    else:
        pass


def submit_essay(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    answered_exam = AnsweredExam.objects.filter(exam=exam, student=request.user)
    answered_exam = AnsweredExam.objects.create(exam=exam, student=request.user)
    questions = Question.objects.filter(exam=exam)
    for question in questions:
        question_answer = request.POST.get(f"question_{question.id}")
        print(question_answer)
        answer = Answers(
            question=question, answer=question_answer, answered_exam=answered_exam
        )
        answer.save()
        return redirect("success")
    return redirect("failed")


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


class SubmittedSuccessfully(TemplateView):
    template_name = "students/success.html"


def join_exam(request):
    exam_pass_code = request.POST.get("pass_code")
    exam_id = request.POST.get("exam_id")
    exam = get_object_or_404(Exam, pk=int(exam_id))
    exams = Exam.objects.all()
    print(exam_pass_code, exam_id)
    if request.POST:
        print(exam_pass_code, exam_id, exams)
        for exam in exams:
            if exam.pass_code == exam_pass_code and exam.pk == int(exam_id):
                student = Students(exam=exam, student=request.user.email)
                student.save()
                messages.success(request, f"You now have access to {student.exam.name}")
                return redirect("student")
    messages.error(request, "Request failed, check the pass code if it is correct")
    return redirect("student")


def already_submitted(request):
    return render(request, "students/Already_submitted.html")
