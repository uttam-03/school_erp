from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'get_name', 'current_class', 'parent_name', 'parent_phone', 'is_active']
    list_filter = ['current_class', 'is_active', 'blood_group']
    search_fields = ['admission_number', 'user__first_name', 'user__last_name', 'user__email', 'parent_name']
    raw_id_fields = ['user']
    def get_name(self, obj): return obj.user.get_full_name()
    get_name.short_description = 'Name'
