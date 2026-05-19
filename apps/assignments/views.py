"""Assignment Views - Fixed"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from apps.classes.models import Class
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from apps.students.models import Student


@login_required
def index(request):
    user = request.user
    if user.is_student_role:
        student = get_object_or_404(Student, user=user)
        if student.current_class:
            # Show ALL assignments for student's class - from any teacher
            assignments = Assignment.objects.filter(
                assigned_class=student.current_class
            ).select_related('subject', 'teacher__user', 'assigned_class').order_by('-created_at')
        else:
            assignments = Assignment.objects.none()
        submitted_ids = list(
            Submission.objects.filter(student=student).values_list('assignment_id', flat=True)
        )
        return render(request, 'assignments/student_list.html', {
            'assignments': assignments,
            'submitted_ids': submitted_ids,
            'student': student,
            'page_title': 'My Assignments',
        })
    elif user.is_teacher:
        teacher = get_object_or_404(Teacher, user=user)
        assignments = Assignment.objects.filter(
            teacher=teacher
        ).select_related('subject', 'assigned_class').order_by('-created_at')
    else:
        assignments = Assignment.objects.select_related(
            'subject', 'assigned_class', 'teacher__user'
        ).order_by('-created_at')
    return render(request, 'assignments/list.html', {
        'assignments': assignments, 'page_title': 'Assignments'
    })


@login_required
def detail(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related('subject', 'assigned_class', 'teacher__user'), pk=pk
    )
    user = request.user
    submission = None
    submissions = None
    if user.is_student_role:
        student = get_object_or_404(Student, user=user)
        submission = Submission.objects.filter(assignment=assignment, student=student).first()
    else:
        submissions = Submission.objects.filter(
            assignment=assignment
        ).select_related('student__user').order_by('-submitted_at')
    return render(request, 'assignments/detail.html', {
        'assignment': assignment, 'submission': submission,
        'submissions': submissions, 'page_title': assignment.title,
    })


@login_required
def create(request):
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('assignments:index')
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        teacher = Teacher.objects.filter(user=request.user).first()
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        subject_id = request.POST.get('subject')
        class_id = request.POST.get('assigned_class')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks', 100) or 100

        if not all([title, description, subject_id, class_id, due_date]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'assignments/form.html', {
                'classes': classes, 'subjects': subjects,
                'page_title': 'New Assignment', 'action': 'create',
            })

        assignment = Assignment.objects.create(
            title=title, description=description,
            subject_id=subject_id, assigned_class_id=class_id,
            teacher=teacher, due_date=due_date, max_marks=max_marks,
        )
        if request.FILES.get('file'):
            assignment.file = request.FILES['file']
            assignment.save()
        messages.success(request, f'Assignment "{title}" created successfully.')
        return redirect('assignments:index')
    return render(request, 'assignments/form.html', {
        'classes': classes, 'subjects': subjects,
        'page_title': 'New Assignment', 'action': 'create',
    })


@login_required
def edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('assignments:index')
    if request.method == 'POST':
        assignment.title = request.POST.get('title', assignment.title)
        assignment.description = request.POST.get('description', assignment.description)
        assignment.due_date = request.POST.get('due_date', assignment.due_date)
        assignment.max_marks = request.POST.get('max_marks', assignment.max_marks)
        if request.FILES.get('file'):
            assignment.file = request.FILES['file']
        assignment.save()
        messages.success(request, 'Assignment updated.')
        return redirect('assignments:detail', pk=pk)
    return render(request, 'assignments/form.html', {
        'assignment': assignment, 'page_title': 'Edit Assignment', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('assignments:index')
    assignment = get_object_or_404(Assignment, pk=pk)
    assignment.delete()
    messages.success(request, 'Assignment deleted.')
    return redirect('assignments:index')


@login_required
def submit(request, pk):
    """Student submits an assignment - file is optional, remarks required."""
    if not request.user.is_student_role:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignments:index')
    assignment = get_object_or_404(Assignment, pk=pk)
    student = get_object_or_404(Student, user=request.user)

    # Check already submitted
    existing = Submission.objects.filter(assignment=assignment, student=student).first()
    if existing and existing.status == 'graded':
        messages.info(request, 'This assignment is already graded.')
        return redirect('assignments:detail', pk=pk)

    if request.method == 'POST':
        remarks = request.POST.get('remarks', '').strip()

        # Must have either a file or remarks
        has_file = bool(request.FILES.get('file'))
        has_remarks = bool(remarks)

        if not has_file and not has_remarks:
            messages.error(request, 'Please upload a file or write a note before submitting.')
            return render(request, 'assignments/submit.html', {
                'assignment': assignment, 'page_title': 'Submit Assignment',
            })

        if existing:
            sub = existing
        else:
            sub = Submission(assignment=assignment, student=student)

        if has_file:
            sub.file = request.FILES['file']
        sub.remarks = remarks
        sub.status = 'late' if assignment.is_overdue else 'submitted'
        sub.submitted_at = timezone.now()
        sub.save()
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('assignments:index')

    return render(request, 'assignments/submit.html', {
        'assignment': assignment,
        'existing': existing,
        'page_title': 'Submit Assignment',
    })


@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('assignments:index')
    if request.method == 'POST':
        marks = request.POST.get('marks_obtained')
        if not marks:
            messages.error(request, 'Please enter marks.')
            return render(request, 'assignments/grade.html', {'submission': submission})
        try:
            marks = float(marks)
            if marks < 0 or marks > submission.assignment.max_marks:
                raise ValueError
        except ValueError:
            messages.error(request, f'Marks must be between 0 and {submission.assignment.max_marks}.')
            return render(request, 'assignments/grade.html', {'submission': submission})
        submission.marks_obtained = marks
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.save()
        messages.success(request, f'Graded: {marks}/{submission.assignment.max_marks}')
        return redirect('assignments:detail', pk=submission.assignment.pk)
    return render(request, 'assignments/grade.html', {'submission': submission})
