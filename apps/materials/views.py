"""Study Materials Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudyMaterial
from apps.classes.models import Class
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from apps.students.models import Student


@login_required
def index(request):
    user = request.user
    subject_filter = request.GET.get('subject', '')

    if user.is_student_role:
        student = Student.objects.filter(user=user).first()
        materials = StudyMaterial.objects.filter(
            academic_class=student.current_class
        ).select_related('subject', 'uploaded_by__user') if student and student.current_class else []
    elif user.is_teacher:
        teacher = Teacher.objects.filter(user=user).first()
        materials = StudyMaterial.objects.filter(
            uploaded_by=teacher
        ).select_related('subject', 'academic_class') if teacher else []
    else:
        materials = StudyMaterial.objects.select_related('subject', 'academic_class', 'uploaded_by__user').all()

    if subject_filter:
        materials = materials.filter(subject_id=subject_filter)

    subjects = Subject.objects.all()
    return render(request, 'materials/list.html', {
        'materials': materials, 'subjects': subjects,
        'subject_filter': subject_filter, 'page_title': 'Study Materials',
    })


@login_required
def detail(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    # Increment download count when viewed
    material.download_count += 1
    material.save(update_fields=['download_count'])
    return render(request, 'materials/detail.html', {'material': material, 'page_title': material.title})


@login_required
def create(request):
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('materials:index')
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        teacher = Teacher.objects.filter(user=request.user).first()
        material = StudyMaterial.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            subject_id=request.POST.get('subject'),
            academic_class_id=request.POST.get('academic_class'),
            uploaded_by=teacher,
            material_type=request.POST.get('material_type', 'pdf'),
            external_link=request.POST.get('external_link', ''),
        )
        if request.FILES.get('file'):
            material.file = request.FILES['file']
            material.save()
        messages.success(request, 'Material uploaded successfully.')
        return redirect('materials:index')
    return render(request, 'materials/form.html', {
        'classes': classes, 'subjects': subjects,
        'types': StudyMaterial.TYPE_CHOICES, 'page_title': 'Upload Material', 'action': 'create',
    })


@login_required
def edit(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('materials:index')
    if request.method == 'POST':
        material.title = request.POST.get('title', material.title)
        material.description = request.POST.get('description', material.description)
        material.external_link = request.POST.get('external_link', material.external_link)
        if request.FILES.get('file'):
            material.file = request.FILES['file']
        material.save()
        messages.success(request, 'Material updated.')
        return redirect('materials:index')
    return render(request, 'materials/form.html', {
        'material': material, 'page_title': 'Edit Material', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('materials:index')
    get_object_or_404(StudyMaterial, pk=pk).delete()
    messages.success(request, 'Material deleted.')
    return redirect('materials:index')
