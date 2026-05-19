from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help = 'Load default time slots'
    def handle(self, *args, **kwargs):
        from apps.timetable.models import TimeSlot
        slots = [
            ('Period 1','08:00','08:45',1),('Period 2','08:45','09:30',2),
            ('Recess','09:30','09:45',3),('Period 3','09:45','10:30',4),
            ('Period 4','10:30','11:15',5),('Lunch','11:15','12:00',6),
            ('Period 5','12:00','12:45',7),('Period 6','12:45','13:30',8),
            ('Period 7','13:30','14:15',9),
        ]
        created = 0
        for name, start, end, order in slots:
            _, new = TimeSlot.objects.get_or_create(name=name, defaults={'start_time':start,'end_time':end,'order':order})
            if new: created += 1
        self.stdout.write(self.style.SUCCESS(f'Done. {created} new slots created.'))
