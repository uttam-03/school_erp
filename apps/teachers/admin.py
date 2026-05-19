from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_name', 'qualification', 'specialization', 'experience_years', 'is_active']
    list_filter = ['is_active', 'is_class_teacher']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    filter_horizontal = ['assigned_classes', 'assigned_subjects']
    def get_name(self, obj): return obj.user.get_full_name()
    get_name.short_description = 'Name'
