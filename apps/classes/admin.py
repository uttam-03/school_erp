from django.contrib import admin
from .models import Class

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'academic_year', 'class_teacher', 'get_student_count', 'max_students']
    list_filter = ['academic_year', 'name']
    search_fields = ['name', 'section']
    filter_horizontal = ['subjects']
    def get_student_count(self, obj): return obj.get_student_count()
    get_student_count.short_description = 'Students'
