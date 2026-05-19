from django.contrib import admin
from .models import StudyMaterial

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'academic_class', 'material_type', 'uploaded_by', 'download_count']
    list_filter = ['material_type', 'subject']
    search_fields = ['title']
