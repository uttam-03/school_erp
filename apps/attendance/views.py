"""Attendance Views - Fixed"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import Attendance
from apps.students.models import Student
from apps.classes.models import Class
from apps.subjects.models import Subject
from apps.teachers.models import Teacher


@login_required
def index(request):
    user = request.user
    date_filter = request.GET.get('date', '')
    class_filter = request.GET.get('class_id', '')

    if user.is_admin:
        records = Attendance.objects.select_related(
            'student__user', 'subject', 'marked_by__user'
        ).order_by('-date')
        if class_filter:
            records = records.filter(student__current_class_id=class_filter)
    elif user.is_teacher:
        teacher = get_object_or_404(Teacher, user=user)
        records = Attendance.objects.filter(
            marked_by=teacher
        ).select_related('student__user', 'subject').order_by('-date')
    else:
        student = get_object_or_404(Student, user=user)
        records = Attendance.objects.filter(
            student=student
        ).select_related('subject').order_by('-date')

    if date_filter:
        records = records.filter(date=date_filter)

    records = records[:200]

    student_stats = None
    if user.is_student_role:
        student = get_object_or_404(Student, user=user)
        all_records = Attendance.objects.filter(student=student)
        total = all_records.count()
        present = all_records.filter(status='present').count()
        absent = all_records.filter(status='absent').count()
        late = all_records.filter(status='late').count()
        student_stats = {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round(present / total * 100, 1) if total else 0,
        }

    classes = Class.objects.all() if user.is_admin else []

    return render(request, 'attendance/index.html', {
        'records': records,
        'student_stats': student_stats,
        'classes': classes,
        'class_filter': class_filter,
        'date_filter': date_filter,
        'page_title': 'Attendance',
    })


@login_required
def create(request):
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, 'Permission denied.')
        return redirect('attendance:index')

    classes = Class.objects.all()
    subjects = Subject.objects.all()
    students = []
    selected_class = None
    selected_subject = None
    selected_date = timezone.now().date()

    # Handle GET - load students for selected class
    if request.method == 'GET':
        class_id = request.GET.get('class_id')
        date_str = request.GET.get('date', '')
        subj_id = request.GET.get('subject_id', '')
        if date_str:
            try:
                from datetime import datetime
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                pass
        if class_id:
            selected_class = get_object_or_404(Class, pk=class_id)
            students = Student.objects.filter(
                current_class=selected_class, is_active=True
            ).select_related('user').order_by('admission_number')
            # Pre-load existing attendance for that date
            if subj_id:
                existing = {
                    a.student_id: a for a in Attendance.objects.filter(
                        student__current_class=selected_class,
                        date=selected_date,
                        subject_id=subj_id
                    )
                }
            else:
                existing = {
                    a.student_id: a for a in Attendance.objects.filter(
                        student__current_class=selected_class,
                        date=selected_date,
                        subject__isnull=True
                    )
                }
            for s in students:
                s.existing_status = existing.get(s.pk, None)

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id', '').strip()
        date_str = request.POST.get('date', str(timezone.now().date()))
        teacher = Teacher.objects.filter(user=request.user).first()

        selected_class = get_object_or_404(Class, pk=class_id)
        subject = Subject.objects.filter(pk=subject_id).first() if subject_id else None
        students_list = Student.objects.filter(current_class=selected_class, is_active=True)

        saved = 0
        for student in students_list:
            status = request.POST.get(f'status_{student.id}', 'absent')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            filter_kwargs = dict(student=student, date=date_str)
            if subject:
                filter_kwargs['subject'] = subject
            else:
                filter_kwargs['subject__isnull'] = True

            Attendance.objects.update_or_create(
                **filter_kwargs,
                defaults={
                    'status': status,
                    'remarks': remarks,
                    'marked_by': teacher,
                    'subject': subject,
                }
            )
            saved += 1

        messages.success(request, f'Attendance marked for {saved} students on {date_str}.')
        return redirect('attendance:index')

    return render(request, 'attendance/mark.html', {
        'classes': classes,
        'subjects': subjects,
        'students': students,
        'selected_class': selected_class,
        'selected_date': selected_date,
        'page_title': 'Mark Attendance',
    })


@login_required
def detail(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    return render(request, 'attendance/detail.html', {'record': record})


@login_required
def edit(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, 'Permission denied.')
        return redirect('attendance:index')
    if request.method == 'POST':
        record.status = request.POST.get('status', record.status)
        record.remarks = request.POST.get('remarks', record.remarks)
        record.save()
        messages.success(request, 'Attendance updated.')
        return redirect('attendance:index')
    return render(request, 'attendance/edit.html', {'record': record})


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Permission denied.')
        return redirect('attendance:index')
    record = get_object_or_404(Attendance, pk=pk)
    record.delete()
    messages.success(request, 'Attendance record deleted.')
    return redirect('attendance:index')
