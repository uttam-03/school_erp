"""Student Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Student
from apps.accounts.models import User
from apps.classes.models import Class


@login_required
def index(request):
    if not (request.user.is_admin or request.user.is_teacher):
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    search = request.GET.get('search', '')
    class_filter = request.GET.get('class_id', '')

    students = Student.objects.select_related('user', 'current_class').filter(is_active=True)
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(admission_number__icontains=search) |
            Q(user__email__icontains=search)
        )
    if class_filter:
        students = students.filter(current_class_id=class_filter)

    paginator = Paginator(students.order_by('admission_number'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    classes = Class.objects.all()

    return render(request, 'students/list.html', {
        'page_obj': page_obj,
        'classes': classes,
        'search': search,
        'class_filter': class_filter,
        'page_title': 'Students',
    })


@login_required
def detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Students can only view their own profile
    if request.user.is_student_role and student.user != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:student')

    from apps.attendance.models import Attendance
    from apps.results.models import Result
    from apps.fees.models import FeeRecord

    attendance_summary = {
        'total': Attendance.objects.filter(student=student).count(),
        'present': Attendance.objects.filter(student=student, status='present').count(),
        'absent': Attendance.objects.filter(student=student, status='absent').count(),
    }
    results = Result.objects.filter(student=student).select_related('exam', 'subject').order_by('-created_at')
    fee_records = FeeRecord.objects.filter(student=student).order_by('-created_at')

    return render(request, 'students/detail.html', {
        'student': student,
        'attendance_summary': attendance_summary,
        'results': results,
        'fee_records': fee_records,
        'page_title': f'Student: {student.user.get_full_name()}',
    })


@login_required
def create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    classes = Class.objects.all()
    if request.method == 'POST':
        # Create user account first
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
        else:
            user = User.objects.create_user(
                email=email,
                username=request.POST.get('admission_number'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                password=request.POST.get('password'),
                role=User.STUDENT,
                phone=request.POST.get('phone', ''),
                is_approved=True,
            )
            class_id = request.POST.get('current_class')
            Student.objects.create(
                user=user,
                admission_number=request.POST.get('admission_number'),
                current_class_id=class_id if class_id else None,
                parent_name=request.POST.get('parent_name', ''),
                parent_phone=request.POST.get('parent_phone', ''),
                parent_email=request.POST.get('parent_email', ''),
                blood_group=request.POST.get('blood_group', ''),
            )
            messages.success(request, f'Student {user.get_full_name()} created successfully.')
            return redirect('students:index')

    return render(request, 'students/form.html', {
        'classes': classes,
        'page_title': 'Add Student',
        'action': 'create',
    })


@login_required
def edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    classes = Class.objects.all()
    if request.method == 'POST':
        student.user.first_name = request.POST.get('first_name', student.user.first_name)
        student.user.last_name = request.POST.get('last_name', student.user.last_name)
        student.user.phone = request.POST.get('phone', student.user.phone)
        student.user.save()
        class_id = request.POST.get('current_class')
        student.current_class_id = class_id if class_id else None
        student.parent_name = request.POST.get('parent_name', student.parent_name)
        student.parent_phone = request.POST.get('parent_phone', student.parent_phone)
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('students:detail', pk=pk)

    return render(request, 'students/form.html', {
        'student': student,
        'classes': classes,
        'page_title': 'Edit Student',
        'action': 'edit',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    student = get_object_or_404(Student, pk=pk)
    student.is_active = False
    student.save()
    messages.success(request, 'Student deactivated.')
    return redirect('students:index')
