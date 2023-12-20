from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Exam, Question, Option, Result, Students
from .forms import QuestionForm, OptionForm, ExamForm, StudentForm, McQuestionForm
from ..students.models import AnsweredExam, Answers
from .decorators import teacher_required
from .mixin import TeacherRequiredMixin
from .utils import send_result_emails


class TeacherView(LoginRequiredMixin, TeacherRequiredMixin, TemplateView):
    template_name = "teachers/teacher.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exams"] = self.request.user.exams.all()
        return context


class ExamCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    template_name = "teachers/create_exam.html"
    model = Exam
    form_class = ExamForm

    success_url = reverse_lazy("create_exam")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, "The task was created successfully.")
        return super(ExamCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exams"] = self.request.user.exams.all()
        return context


@login_required
@teacher_required
def create_exam(request):
    if request.method == "POST":
        exam_form = ExamForm(request.POST)
        if exam_form.is_valid():
            exam = exam_form.save(commit=False)
            exam.teacher = request.user
            exam.save()
            messages.success(request, "The Exam was created successfully.")
        if exam_form.errors:
            messages.error(
                request, f"Exam was not created because {exam_form.errors.as_text()}"
            )

    exams = request.user.exams.all()
    return render(request, "teachers/create_exam.html", {"exams": exams})


@login_required
@teacher_required
def essay_question_create_page(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.exam_type == "essay":
        print("passed")
        question_form = QuestionForm(request.POST or None)

        if request.method == "POST":
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.exam = exam
                question.save()
                question_form = QuestionForm()

        questions = exam.questions.all()
        context = {"questions": questions, "form": question_form, "exam": exam}
        return render(request, "teachers/create_essay_questions.html", context)
    messages.error(request, f"{exam.name} is not an essay question")
    return redirect("create_exam")


@login_required
@teacher_required
def essay_question_create(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    question_form = QuestionForm(request.POST)
    if request.method == "POST":
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, "The Question was created successfully.")
            return render(
                request, "partials/questions.html", {"questions": exam.questions.all()}
            )
        messages.error(
            request, f"Questions was not added {question_form.errors.as_text()}"
        )
        return render(
            request, "partials/questions.html", {"questions": exam.questions.all()}
        )


@login_required
@teacher_required
def multiple_choice_quections(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.exam_type == "mc":
        question_form = McQuestionForm(request.POST or None)

        if request.method == "POST":
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.exam = exam
                question.save()
                option = request.POST.get("option")
                option = Option.objects.create(
                    question=question, name=option, is_answer=True
                )
                question_form = McQuestionForm()

        questions = exam.questions.all()
        context = {
            "questions": questions,
            "form": question_form,
            "message": messages,
            "option_form": OptionForm(),
            "exam": exam,
        }
        return render(request, "teachers/create_mm_questions.html", context)
    messages.error(request, f"{exam.name} is not a multiple choice exam")
    return redirect("create_exam")


@login_required
@teacher_required
def written_scripts(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    answers = AnsweredExam.objects.filter(exam=exam)
    return render(request, "teachers/mark.html", {"exam": exam, "answers": answers})


@login_required
@teacher_required
def written_script_mark(request, answered_exam_id):
    answered_exam = get_object_or_404(AnsweredExam, pk=answered_exam_id)
    answers = answered_exam.exam_answers.all()
    return render(
        request,
        "teachers/mark_student.html",
        {"exam": answered_exam, "answers": answers},
    )


@login_required
@teacher_required
def mark(request, answer_exam_id):
    answer_exam = get_object_or_404(AnsweredExam, pk=answer_exam_id)
    answers = Answers.objects.filter(answered_exam=answer_exam)
    total_score = 0
    for answer in answers:
        answer_comment = request.POST.get(f"comment_{answer.id}")
        answer_marks = request.POST.get(f"marks{answer.id}")
        answer.comment = answer_comment
        answer.score = float(answer_marks)
        answer.save()
        total_score = total_score + float(answer_marks)
    total_score = total_score / 100
    result = Result(
        student=answer_exam.student, exam=answer_exam.exam, total_marks=total_score
    )
    result.save()

    return redirect("scripts", answer_exam.exam.pk)


@login_required
@teacher_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    exam.delete()
    messages.success(request, f"{exam.name} deleted successfully")
    return redirect(reverse("create_exam"))


@login_required
@teacher_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    exam_question = question.exam
    question.delete()
    messages.success(request, f"{question.question} deleted successfully")
    return redirect("create_essay_questions", exam_question.pk)


@login_required
@teacher_required
def delete_mc_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    exam_question = question.exam
    question.delete()
    messages.success(request, f"{question.question} deleted successfully")
    return redirect("create_mc_questions", exam_question.pk)


@login_required
@teacher_required
def add_option_to_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == "POST":
        option_form = OptionForm(request.POST)
        if option_form.is_valid():
            option = option_form.save(commit=False)
            option.question = question
            option.save()
            messages.success(request, "The Option was created successfully.")
            return render(
                request, "partials/options.html", {"options": question.options.all()}
            )
        else:
            messages.error(request, "Invalid data. The Option creation failed.")
    else:
        option_form = OptionForm()

    return render(
        request,
        "partials/options.html",
        {"options": question.options.all(), "option_form": option_form},
    )


@login_required
@teacher_required
def delete_option(request, option_id):
    option = get_object_or_404(Option, pk=option_id)
    question_id = option.question.id
    option.delete()

    options = Option.objects.filter(question_id=question_id)

    return render(
        request,
        "partials/options.html",
        {"options": options, "question_id": question_id},
    )


class StudentsCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    template_name = "teachers/register_student.html"
    form_class = StudentForm
    context_object_name = "students"


@login_required
@teacher_required
def students_create(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    student_form = StudentForm(request.POST or None)
    students = Students.objects.filter(exam=exam)
    print(student_form.errors.as_json())
    if request.method == "POST":
        if student_form.is_valid():
            student = student_form.save(commit=False)
            student.exam = exam
            student.save()
            messages.success(
                request, f"{student.student} has been granted access to the exam"
            )
        else:
            messages.error(
                request, f"operation has failed, {student_form.errors.as_text()}"
            )
    return render(
        request,
        "teachers/register_student.html",
        {"exam": exam, "student_form": student_form, "students": students},
    )


@login_required
@teacher_required
def results_view(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    results = Result.objects.filter(exam=exam)
    return render(request, "teachers/results.html", {"exam": exam, "results": results})


@login_required
@teacher_required
def send_emails(request, exam_id):
    send_result_emails(exam_id=exam_id)
    messages.success(request, f"Emails sent successfully")
    return redirect("results_view", exam_id)


@login_required
@teacher_required
def delete_student(request, student_id, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    student = get_object_or_404(Students, pk=student_id, exam=exam)
    if student.exam.teacher == request.user:
        student.delete()
        messages.success(request, f"Student deleted successfully")
        return redirect("students_create", student.exam.id)
    messages.error(request, f"You cannot delete things you did not create")
    return redirect("teacher")
