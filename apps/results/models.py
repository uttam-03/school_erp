"""Result Models"""

from django.db import models


class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'),
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'F'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    total_marks = models.PositiveIntegerField()
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    remarks = models.CharField(max_length=255, blank=True)
    entered_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'results'
        unique_together = ['student', 'exam', 'subject']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.exam.name} - {self.marks_obtained}/{self.total_marks}"

    @property
    def percentage(self):
        return round((float(self.marks_obtained) / self.total_marks * 100), 2) if self.total_marks else 0

    @property
    def is_pass(self):
        return self.marks_obtained >= self.exam.passing_marks

    def save(self, *args, **kwargs):
        pct = self.percentage
        if pct >= 90: self.grade = 'A+'
        elif pct >= 80: self.grade = 'A'
        elif pct >= 70: self.grade = 'B+'
        elif pct >= 60: self.grade = 'B'
        elif pct >= 50: self.grade = 'C+'
        elif pct >= 40: self.grade = 'C'
        elif pct >= 35: self.grade = 'D'
        else: self.grade = 'F'
        super().save(*args, **kwargs)
