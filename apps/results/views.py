"""Results Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Result
from apps.exams.models import Exam
from apps.students.models import Student
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from apps.classes.models import Class


@login_required
def index(request):
    user = request.user
    if user.is_student_role:
        student = get_object_or_404(Student, user=user)
        results = Result.objects.filter(student=student).select_related('exam', 'subject').order_by('-created_at')
    elif user.is_teacher:
        teacher = get_object_or_404(Teacher, user=user)
        results = Result.objects.filter(entered_by=teacher).select_related('student__user', 'exam', 'subject').order_by('-created_at')
    else:
        results = Result.objects.select_related('student__user', 'exam', 'subject').order_by('-created_at')

    paginator = Paginator(results, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'results/list.html', {'page_obj': page_obj, 'page_title': 'Results'})


@login_required
def detail(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.user.is_student_role:
        student = get_object_or_404(Student, user=request.user)
        if result.student != student:
            messages.error(request, 'Access denied.')
            return redirect('results:index')
    return render(request, 'results/detail.html', {'result': result, 'page_title': 'Result Detail'})


@login_required
def create(request):
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('results:index')
    classes = Class.objects.all()
    exams = Exam.objects.select_related('subject', 'academic_class').order_by('-exam_date')
    students = []
    selected_class = None
    selected_exam = None

    if request.GET.get('class_id'):
        selected_class = get_object_or_404(Class, pk=request.GET['class_id'])
        students = Student.objects.filter(current_class=selected_class, is_active=True).select_related('user')
    if request.GET.get('exam_id'):
        selected_exam = get_object_or_404(Exam, pk=request.GET['exam_id'])

    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = get_object_or_404(Exam, pk=exam_id)
        teacher = Teacher.objects.filter(user=request.user).first()
        saved = 0
        students_list = Student.objects.filter(current_class=exam.academic_class, is_active=True)
        for student in students_list:
            marks = request.POST.get(f'marks_{student.id}')
            if marks:
                Result.objects.update_or_create(
                    student=student, exam=exam, subject=exam.subject,
                    defaults={
                        'marks_obtained': marks,
                        'total_marks': exam.total_marks,
                        'entered_by': teacher,
                    }
                )
                saved += 1
        messages.success(request, f'Results saved for {saved} students.')
        return redirect('results:index')

    return render(request, 'results/form.html', {
        'classes': classes, 'exams': exams, 'students': students,
        'selected_class': selected_class, 'selected_exam': selected_exam,
        'page_title': 'Enter Results',
    })


@login_required
def edit(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('results:index')
    if request.method == 'POST':
        result.marks_obtained = request.POST.get('marks_obtained', result.marks_obtained)
        result.remarks = request.POST.get('remarks', result.remarks)
        result.save()
        messages.success(request, 'Result updated.')
        return redirect('results:index')
    return render(request, 'results/edit.html', {'result': result, 'page_title': 'Edit Result'})


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('results:index')
    get_object_or_404(Result, pk=pk).delete()
    messages.success(request, 'Result deleted.')
    return redirect('results:index')
