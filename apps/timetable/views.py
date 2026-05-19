"""Timetable Views - Fixed grid rendering"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Timetable, TimeSlot
from apps.classes.models import Class
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from apps.students.models import Student


DAYS = [('Mon','Monday'),('Tue','Tuesday'),('Wed','Wednesday'),
        ('Thu','Thursday'),('Fri','Friday'),('Sat','Saturday')]
DAY_KEYS = [d[0] for d in DAYS]


@login_required
def index(request):
    user = request.user
    selected_class = None
    time_slots = TimeSlot.objects.all().order_by('order')
    classes = Class.objects.all()

    # Auto-select class based on role
    if user.is_student_role:
        student = Student.objects.filter(user=user).first()
        if student and student.current_class:
            selected_class = student.current_class
    elif user.is_teacher:
        teacher = Teacher.objects.filter(user=user).first()
        if teacher:
            class_id = request.GET.get('class_id')
            if class_id:
                selected_class = get_object_or_404(Class, pk=class_id)
                # Ensure teacher is assigned to this class
                if selected_class not in teacher.assigned_classes.all():
                    selected_class = teacher.assigned_classes.first()
            else:
                selected_class = teacher.assigned_classes.first()
            classes = teacher.assigned_classes.all()
    else:
        class_id = request.GET.get('class_id')
        if class_id:
            selected_class = get_object_or_404(Class, pk=class_id)

    # Build grid: {day_key: {slot_id: timetable_entry}}
    grid = {day: {} for day in DAY_KEYS}
    timetable_qs = []

    if selected_class:
        timetable_qs = Timetable.objects.filter(
            academic_class=selected_class
        ).select_related('subject', 'teacher__user', 'time_slot').order_by('time_slot__order')

        for entry in timetable_qs:
            if entry.day in grid:
                grid[entry.day][entry.time_slot_id] = entry

    return render(request, 'timetable/index.html', {
        'selected_class': selected_class,
        'classes': classes,
        'timetable': timetable_qs,
        'grid': grid,
        'days': DAYS,
        'day_keys': DAY_KEYS,
        'time_slots': time_slots,
        'page_title': 'Timetable',
    })


@login_required
def create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('timetable:index')
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    time_slots = TimeSlot.objects.all().order_by('order')

    if not time_slots.exists():
        messages.warning(request, 'No time slots found. Run: python manage.py load_timeslots')

    if request.method == 'POST':
        academic_class_id = request.POST.get('academic_class')
        day = request.POST.get('day')
        time_slot_id = request.POST.get('time_slot')
        academic_year = request.POST.get('academic_year', '').strip()

        if not all([academic_class_id, day, time_slot_id, academic_year]):
            messages.error(request, 'Please fill all required fields.')
        else:
            Timetable.objects.update_or_create(
                academic_class_id=academic_class_id,
                day=day,
                time_slot_id=time_slot_id,
                academic_year=academic_year,
                defaults={
                    'subject_id': request.POST.get('subject'),
                    'teacher_id': request.POST.get('teacher'),
                    'room': request.POST.get('room', ''),
                }
            )
            messages.success(request, 'Timetable entry saved.')
            return redirect('timetable:index')

    return render(request, 'timetable/form.html', {
        'classes': classes, 'subjects': subjects, 'teachers': teachers,
        'time_slots': time_slots, 'days': DAYS, 'page_title': 'Add Timetable Entry',
    })


@login_required
def detail(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    return render(request, 'timetable/detail.html', {'entry': entry})


@login_required
def edit(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('timetable:index')
    if request.method == 'POST':
        entry.subject_id = request.POST.get('subject', entry.subject_id)
        entry.teacher_id = request.POST.get('teacher', entry.teacher_id)
        entry.room = request.POST.get('room', entry.room)
        entry.save()
        messages.success(request, 'Timetable updated.')
        return redirect('timetable:index')
    return render(request, 'timetable/form.html', {
        'entry': entry,
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': Teacher.objects.filter(is_active=True).select_related('user'),
        'time_slots': TimeSlot.objects.all().order_by('order'),
        'days': DAYS,
        'page_title': 'Edit Timetable Entry',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('timetable:index')
    get_object_or_404(Timetable, pk=pk).delete()
    messages.success(request, 'Entry deleted.')
    return redirect('timetable:index')
