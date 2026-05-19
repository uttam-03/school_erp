"""Teacher Models"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    assigned_classes = models.ManyToManyField(
        'classes.Class', blank=True, related_name='teachers'
    )
    assigned_subjects = models.ManyToManyField(
        'subjects.Subject', blank=True, related_name='teachers'
    )
    is_active = models.BooleanField(default=True)
    is_class_teacher = models.BooleanField(default=False)

    class Meta:
        db_table = 'teachers'
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
