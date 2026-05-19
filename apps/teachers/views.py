"""Teacher Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Teacher
from apps.accounts.models import User
from apps.classes.models import Class
from apps.subjects.models import Subject


@login_required
def index(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    search = request.GET.get('search', '')
    teachers = Teacher.objects.select_related('user').filter(is_active=True)
    if search:
        teachers = teachers.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(specialization__icontains=search)
        )
    paginator = Paginator(teachers.order_by('employee_id'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'teachers/list.html', {
        'page_obj': page_obj, 'search': search, 'page_title': 'Teachers',
    })


@login_required
def detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    from apps.assignments.models import Assignment
    from apps.attendance.models import Attendance
    from django.utils import timezone
    today = timezone.now().date()
    return render(request, 'teachers/detail.html', {
        'teacher': teacher,
        'assignments': Assignment.objects.filter(teacher=teacher).order_by('-created_at')[:5],
        'today_attendance': Attendance.objects.filter(marked_by=teacher, date=today).count(),
        'page_title': f'Teacher: {teacher.user.get_full_name()}',
    })


@login_required
def create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
        else:
            user = User.objects.create_user(
                email=email,
                username=request.POST.get('employee_id'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                password=request.POST.get('password'),
                role=User.TEACHER,
                phone=request.POST.get('phone', ''),
                is_approved=True,
            )
            teacher = Teacher.objects.create(
                user=user,
                employee_id=request.POST.get('employee_id'),
                qualification=request.POST.get('qualification', ''),
                specialization=request.POST.get('specialization', ''),
                experience_years=request.POST.get('experience_years', 0),
                joining_date=request.POST.get('joining_date'),
                salary=request.POST.get('salary', 0),
            )
            class_ids = request.POST.getlist('assigned_classes')
            subject_ids = request.POST.getlist('assigned_subjects')
            if class_ids:
                teacher.assigned_classes.set(class_ids)
            if subject_ids:
                teacher.assigned_subjects.set(subject_ids)
            messages.success(request, f'Teacher {user.get_full_name()} created successfully.')
            return redirect('teachers:index')
    return render(request, 'teachers/form.html', {
        'classes': classes, 'subjects': subjects,
        'page_title': 'Add Teacher', 'action': 'create',
    })


@login_required
def edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        teacher.user.first_name = request.POST.get('first_name', teacher.user.first_name)
        teacher.user.last_name = request.POST.get('last_name', teacher.user.last_name)
        teacher.user.phone = request.POST.get('phone', teacher.user.phone)
        teacher.user.save()
        teacher.qualification = request.POST.get('qualification', teacher.qualification)
        teacher.specialization = request.POST.get('specialization', teacher.specialization)
        teacher.experience_years = request.POST.get('experience_years', teacher.experience_years)
        teacher.salary = request.POST.get('salary', teacher.salary)
        class_ids = request.POST.getlist('assigned_classes')
        subject_ids = request.POST.getlist('assigned_subjects')
        teacher.assigned_classes.set(class_ids)
        teacher.assigned_subjects.set(subject_ids)
        teacher.save()
        messages.success(request, 'Teacher updated successfully.')
        return redirect('teachers:detail', pk=pk)
    return render(request, 'teachers/form.html', {
        'teacher': teacher, 'classes': classes, 'subjects': subjects,
        'page_title': 'Edit Teacher', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = False
    teacher.save()
    messages.success(request, 'Teacher deactivated.')
    return redirect('teachers:index')
