from django.contrib import admin
from .models import Assignment, Submission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'assigned_class', 'teacher', 'due_date', 'max_marks']
    list_filter = ['subject', 'assigned_class']
    search_fields = ['title']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'status', 'marks_obtained', 'submitted_at']
    list_filter = ['status']
