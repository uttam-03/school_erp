"""Class Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Class
from apps.subjects.models import Subject
from apps.teachers.models import Teacher


@login_required
def index(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    classes = Class.objects.prefetch_related('students', 'teachers', 'subjects').all()
    return render(request, 'classes/list.html', {'classes': classes, 'page_title': 'Classes'})


@login_required
def detail(request, pk):
    cls = get_object_or_404(Class, pk=pk)
    students = cls.students.filter(is_active=True).select_related('user')
    timetable = cls.timetable.select_related('subject', 'teacher__user', 'time_slot').order_by('day', 'time_slot__order')
    return render(request, 'classes/detail.html', {
        'cls': cls, 'students': students, 'timetable': timetable, 'page_title': str(cls),
    })


@login_required
def create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    subjects = Subject.objects.all()
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    if request.method == 'POST':
        cls = Class.objects.create(
            name=request.POST.get('name'),
            section=request.POST.get('section'),
            academic_year=request.POST.get('academic_year'),
            room_number=request.POST.get('room_number', ''),
            max_students=request.POST.get('max_students', 40),
            class_teacher_id=request.POST.get('class_teacher') or None,
        )
        subject_ids = request.POST.getlist('subjects')
        if subject_ids:
            cls.subjects.set(subject_ids)
        messages.success(request, f'Class {cls} created successfully.')
        return redirect('classes:index')
    return render(request, 'classes/form.html', {
        'subjects': subjects, 'teachers': teachers,
        'page_title': 'Add Class', 'action': 'create',
    })


@login_required
def edit(request, pk):
    cls = get_object_or_404(Class, pk=pk)
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    subjects = Subject.objects.all()
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    if request.method == 'POST':
        cls.name = request.POST.get('name', cls.name)
        cls.section = request.POST.get('section', cls.section)
        cls.academic_year = request.POST.get('academic_year', cls.academic_year)
        cls.room_number = request.POST.get('room_number', cls.room_number)
        cls.max_students = request.POST.get('max_students', cls.max_students)
        cls.class_teacher_id = request.POST.get('class_teacher') or None
        cls.save()
        subject_ids = request.POST.getlist('subjects')
        cls.subjects.set(subject_ids)
        messages.success(request, 'Class updated successfully.')
        return redirect('classes:detail', pk=pk)
    return render(request, 'classes/form.html', {
        'cls': cls, 'subjects': subjects, 'teachers': teachers,
        'page_title': 'Edit Class', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    cls = get_object_or_404(Class, pk=pk)
    cls.delete()
    messages.success(request, 'Class deleted.')
    return redirect('classes:index')
