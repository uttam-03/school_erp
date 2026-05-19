"""Subject Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Subject


@login_required
def index(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    subjects = Subject.objects.all()
    return render(request, 'subjects/list.html', {'subjects': subjects, 'page_title': 'Subjects'})


@login_required
def detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'subjects/detail.html', {'subject': subject, 'page_title': subject.name})


@login_required
def create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    if request.method == 'POST':
        Subject.objects.create(
            name=request.POST.get('name'),
            code=request.POST.get('code'),
            description=request.POST.get('description', ''),
            max_marks=request.POST.get('max_marks', 100),
            passing_marks=request.POST.get('passing_marks', 35),
            is_elective='is_elective' in request.POST,
        )
        messages.success(request, 'Subject created.')
        return redirect('subjects:index')
    return render(request, 'subjects/form.html', {'page_title': 'Add Subject', 'action': 'create'})


@login_required
def edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    if request.method == 'POST':
        subject.name = request.POST.get('name', subject.name)
        subject.code = request.POST.get('code', subject.code)
        subject.description = request.POST.get('description', subject.description)
        subject.max_marks = request.POST.get('max_marks', subject.max_marks)
        subject.passing_marks = request.POST.get('passing_marks', subject.passing_marks)
        subject.is_elective = 'is_elective' in request.POST
        subject.save()
        messages.success(request, 'Subject updated.')
        return redirect('subjects:index')
    return render(request, 'subjects/form.html', {
        'subject': subject, 'page_title': 'Edit Subject', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    get_object_or_404(Subject, pk=pk).delete()
    messages.success(request, 'Subject deleted.')
    return redirect('subjects:index')
