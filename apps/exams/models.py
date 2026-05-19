"""Exam Models"""

from django.db import models


class Exam(models.Model):
    EXAM_TYPES = [
        ('unit_test', 'Unit Test'),
        ('midterm', 'Mid Term'),
        ('final', 'Final Exam'),
        ('practical', 'Practical'),
        ('assignment', 'Assignment'),
    ]

    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    academic_class = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='exams')
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=35)
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exams'
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.name} - {self.subject.name} ({self.academic_class})"
