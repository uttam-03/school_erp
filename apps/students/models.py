"""Student Models"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=20, unique=True)
    current_class = models.ForeignKey(
        'classes.Class', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='students'
    )
    parent_name = models.CharField(max_length=200)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    enrolled_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'students'
        ordering = ['admission_number']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"

    def get_attendance_percentage(self):
        from apps.attendance.models import Attendance
        total = Attendance.objects.filter(student=self).count()
        present = Attendance.objects.filter(student=self, status='present').count()
        return round((present / total * 100), 1) if total else 0
