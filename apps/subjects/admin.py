from django.contrib import admin
from .models import Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'max_marks', 'passing_marks', 'is_elective']
    list_filter = ['is_elective']
    search_fields = ['name', 'code']
