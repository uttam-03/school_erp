"""Study Materials Models"""

from django.db import models


class StudyMaterial(models.Model):
    TYPE_CHOICES = [
        ('notes', 'Notes'),
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('slides', 'Slides'),
        ('link', 'External Link'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='materials')
    academic_class = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='materials')
    uploaded_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='materials')
    material_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='pdf')
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_materials'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.subject.name})"
