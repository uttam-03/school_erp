"""Class and Section Models"""

from django.db import models


class Class(models.Model):
    name = models.CharField(max_length=50)           # e.g. "Grade 10"
    section = models.CharField(max_length=10)         # e.g. "A"
    academic_year = models.CharField(max_length=10)  # e.g. "2024-25"
    room_number = models.CharField(max_length=20, blank=True)
    max_students = models.PositiveIntegerField(default=40)
    subjects = models.ManyToManyField('subjects.Subject', blank=True, related_name='classes')
    class_teacher = models.ForeignKey(
        'teachers.Teacher', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='class_teacher_of'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classes'
        unique_together = ['name', 'section', 'academic_year']
        ordering = ['name', 'section']

    def __str__(self):
        return f"{self.name} - {self.section} ({self.academic_year})"

    def get_student_count(self):
        return self.students.filter(is_active=True).count()
