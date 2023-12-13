from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

from .models import Exam, Question, Option, Result, Students
from .forms import QuestionForm, OptionForm, ExamForm, StudentForm
from ..students.models import AnsweredExam, Answers


class TeacherView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "teachers/teacher.html"

    def test_func(self):
        return self.request.user.is_teacher

    def handle_no_permission(self):
        return redirect(reverse("student"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exams"] = self.request.user.exams.all()
        return context


class ExamCreateView(CreateView):
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


def create_exam(request):
    if request.method == "POST":
        exam_form = ExamForm(request.POST)
        print(exam_form.errors.as_json())
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


def essay_question_create_page(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
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


def multiple_choice_quections(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    question_form = QuestionForm(request.POST or None)

    if request.method == "POST":
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.exam = exam
            question.save()
            question_form = QuestionForm()

    questions = exam.questions.all()
    context = {
        "questions": questions,
        "form": question_form,
        "message": messages,
        "option_form": OptionForm(),
    }
    return render(request, "teachers/create_mm_questions.html", context)


def add_option_to_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    option_form = OptionForm(request.POST)
    if request.method == "POST":
        if option_form.is_valid():
            option = option_form.save(commit=False)
            option.question = question
            option.save()
            return redirect("create_mc_questions", question.exam.pk)
    redirect("create_mc_questions", question.exam.pk)


def written_scripts(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    answers = AnsweredExam.objects.filter(exam=exam)
    return render(request, "teachers/mark.html", {"exam": exam, "answers": answers})


def written_script_mark(request, answered_exam_id):
    answered_exam = get_object_or_404(AnsweredExam, pk=answered_exam_id)
    answers = answered_exam.exam_answers.all()
    return render(
        request,
        "teachers/mark_student.html",
        {"exam": answered_exam, "answers": answers},
    )


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


def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    exam.delete()
    messages.success(request, f"{exam.name} deleted successfully")
    return redirect(reverse("create_exam"))


def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    exam_question = question.exam
    question.delete()
    messages.success(request, f"{question.question} deleted successfully")
    return redirect("create_essay_questions", exam_question.pk)


def add_option_to_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    option_form = OptionForm(request.POST)

    if request.method == "POST":
        if option_form.is_valid():
            option = option_form.save(commit=False)
            option.question = question
            option.save()

            # Render the updated options as HTML
            messages.success(request, "The Option was created successfully.")
            return render(
                request, "partials/options.html", {"options": question.options.all()}
            )

    messages.error(request, "The Option creation failed.")
    return render(request, "partials/options.html", {"options": question.options.all()})


def delete_option(request, option_id):
    option = get_object_or_404(Option, pk=option_id)
    question_id = (
        option.question.id
    )  # Assuming Option model has a ForeignKey field 'question'
    option.delete()

    # Return updated options as HTML
    options = Option.objects.filter(question_id=question_id)

    return render(
        request,
        "partials/options.html",
        {"options": options, "question_id": question_id},
    )


class StudentsCreateView(CreateView):
    template_name = "teachers/register_student.html"
    form_class = StudentForm
    context_object_name = "students"


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
