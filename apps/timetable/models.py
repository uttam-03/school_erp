"""Timetable Models"""

from django.db import models


class TimeSlot(models.Model):
    name = models.CharField(max_length=50)   # e.g. "Period 1"
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'time_slots'
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"


class Timetable(models.Model):
    DAYS = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'),
    ]

    academic_class = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='timetable')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    room = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=10)

    class Meta:
        db_table = 'timetable'
        unique_together = ['academic_class', 'day', 'time_slot', 'academic_year']
        ordering = ['day', 'time_slot__order']

    def __str__(self):
        return f"{self.academic_class} | {self.day} | {self.time_slot} | {self.subject}"
