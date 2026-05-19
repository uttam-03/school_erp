from django.contrib import admin
from .models import Timetable, TimeSlot

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'order']
    ordering = ['order']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['academic_class', 'day', 'time_slot', 'subject', 'teacher', 'room']
    list_filter = ['academic_class', 'day']
