"""Exams Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exam
from apps.classes.models import Class
from apps.subjects.models import Subject
from apps.teachers.models import Teacher


@login_required
def index(request):
    user = request.user
    if user.is_student_role:
        from apps.students.models import Student
        student = get_object_or_404(Student, user=user)
        exams = Exam.objects.filter(
            academic_class=student.current_class
        ).select_related('subject', 'academic_class').order_by('-exam_date') if student.current_class else []
    elif user.is_teacher:
        teacher = get_object_or_404(Teacher, user=user)
        exams = Exam.objects.filter(created_by=teacher).select_related('subject', 'academic_class').order_by('-exam_date')
    else:
        exams = Exam.objects.select_related('subject', 'academic_class').order_by('-exam_date')

    return render(request, 'exams/list.html', {'exams': exams, 'page_title': 'Exams'})


@login_required
def detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    results = exam.results.select_related('student__user').order_by('-marks_obtained')
    return render(request, 'exams/detail.html', {
        'exam': exam, 'results': results, 'page_title': exam.name,
    })


@login_required
def create(request):
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('exams:index')
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        teacher = Teacher.objects.filter(user=request.user).first()
        Exam.objects.create(
            name=request.POST.get('name'),
            exam_type=request.POST.get('exam_type'),
            academic_class_id=request.POST.get('academic_class'),
            subject_id=request.POST.get('subject'),
            exam_date=request.POST.get('exam_date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            total_marks=request.POST.get('total_marks', 100),
            passing_marks=request.POST.get('passing_marks', 35),
            instructions=request.POST.get('instructions', ''),
            created_by=teacher,
        )
        messages.success(request, 'Exam scheduled successfully.')
        return redirect('exams:index')
    return render(request, 'exams/form.html', {
        'classes': classes, 'subjects': subjects,
        'exam_types': Exam.EXAM_TYPES, 'page_title': 'Schedule Exam', 'action': 'create',
    })


@login_required
def edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('exams:index')
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        exam.name = request.POST.get('name', exam.name)
        exam.exam_type = request.POST.get('exam_type', exam.exam_type)
        exam.academic_class_id = request.POST.get('academic_class', exam.academic_class_id)
        exam.subject_id = request.POST.get('subject', exam.subject_id)
        exam.exam_date = request.POST.get('exam_date', exam.exam_date)
        exam.total_marks = request.POST.get('total_marks', exam.total_marks)
        exam.passing_marks = request.POST.get('passing_marks', exam.passing_marks)
        exam.instructions = request.POST.get('instructions', exam.instructions)
        exam.save()
        messages.success(request, 'Exam updated.')
        return redirect('exams:detail', pk=pk)
    return render(request, 'exams/form.html', {
        'exam': exam, 'classes': classes, 'subjects': subjects,
        'exam_types': Exam.EXAM_TYPES, 'page_title': 'Edit Exam', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('exams:index')
    get_object_or_404(Exam, pk=pk).delete()
    messages.success(request, 'Exam deleted.')
    return redirect('exams:index')
