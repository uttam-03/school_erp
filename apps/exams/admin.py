from django.contrib import admin
from .models import Exam

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_class', 'subject', 'exam_date', 'total_marks']
    list_filter = ['exam_type', 'academic_class', 'subject']
    search_fields = ['name']
    date_hierarchy = 'exam_date'
