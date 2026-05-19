from django.contrib import admin
from .models import Result

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'marks_obtained', 'total_marks', 'grade', 'is_pass']
    list_filter = ['grade', 'exam', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name']
