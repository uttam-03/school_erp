"""
Management command to populate the database with sample data.
Run: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample school data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding database...'))

        # ── Subjects ──────────────────────────────────────────────
        from apps.subjects.models import Subject
        subjects_data = [
            ('Mathematics', 'MATH101', 100, 35),
            ('English', 'ENG101', 100, 35),
            ('Science', 'SCI101', 100, 35),
            ('History', 'HIS101', 100, 35),
            ('Geography', 'GEO101', 100, 35),
            ('Computer Science', 'CS101', 100, 35),
            ('Physics', 'PHY101', 100, 35),
            ('Chemistry', 'CHEM101', 100, 35),
        ]
        subjects = []
        for name, code, max_m, pass_m in subjects_data:
            sub, _ = Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'max_marks': max_m, 'passing_marks': pass_m}
            )
            subjects.append(sub)
        self.stdout.write(f'  ✓ {len(subjects)} subjects created')

        # ── Admin User ────────────────────────────────────────────
        admin_user, created = User.objects.get_or_create(
            email='admin@school.com',
            defaults={
                'username': 'admin',
                'first_name': 'System',
                'last_name': 'Admin',
                'role': User.ADMIN,
                'is_approved': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        self.stdout.write('  ✓ Admin user: admin@school.com / admin123')

        # ── Teacher Users ─────────────────────────────────────────
        from apps.teachers.models import Teacher
        teachers_data = [
            ('teacher@school.com', 'Rajesh', 'Kumar', 'TCH001', 'M.Sc Mathematics', 'Mathematics', 8),
            ('priya@school.com', 'Priya', 'Sharma', 'TCH002', 'M.A English', 'English Literature', 5),
            ('amit@school.com', 'Amit', 'Singh', 'TCH003', 'M.Sc Physics', 'Physics', 10),
            ('sunita@school.com', 'Sunita', 'Patel', 'TCH004', 'M.Sc Chemistry', 'Chemistry', 7),
        ]
        teacher_objs = []
        for email, fn, ln, emp_id, qual, spec, exp in teachers_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': emp_id.lower(),
                    'first_name': fn, 'last_name': ln,
                    'role': User.TEACHER, 'is_approved': True,
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
            teacher, _ = Teacher.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'user': user, 'qualification': qual,
                    'specialization': spec, 'experience_years': exp,
                    'joining_date': datetime.date(2020, 6, 1), 'salary': 45000,
                }
            )
            teacher_objs.append(teacher)
        self.stdout.write(f'  ✓ {len(teacher_objs)} teachers created (password: teacher123)')

        # ── Classes ───────────────────────────────────────────────
        from apps.classes.models import Class
        classes_data = [
            ('Grade 9', 'A', '2024-25', '101'),
            ('Grade 9', 'B', '2024-25', '102'),
            ('Grade 10', 'A', '2024-25', '201'),
            ('Grade 10', 'B', '2024-25', '202'),
            ('Grade 11', 'A', '2024-25', '301'),
            ('Grade 12', 'A', '2024-25', '401'),
        ]
        class_objs = []
        for name, section, year, room in classes_data:
            cls, _ = Class.objects.get_or_create(
                name=name, section=section, academic_year=year,
                defaults={'room_number': room, 'max_students': 40}
            )
            cls.subjects.set(random.sample(subjects, min(5, len(subjects))))
            class_objs.append(cls)

        # Assign teachers to classes
        for i, teacher in enumerate(teacher_objs):
            assigned = class_objs[i:i+2] if i+2 <= len(class_objs) else class_objs[i:]
            teacher.assigned_classes.set(assigned)
            teacher.assigned_subjects.set(subjects[i:i+2])

        # Set class teachers
        for i, cls in enumerate(class_objs[:4]):
            if i < len(teacher_objs):
                cls.class_teacher = teacher_objs[i]
                cls.save()

        self.stdout.write(f'  ✓ {len(class_objs)} classes created')

        # ── Students ──────────────────────────────────────────────
        from apps.students.models import Student
        student_names = [
            ('Arjun', 'Sharma'), ('Priya', 'Patel'), ('Rahul', 'Gupta'),
            ('Anjali', 'Singh'), ('Vikram', 'Mehta'), ('Pooja', 'Joshi'),
            ('Rohan', 'Verma'), ('Sneha', 'Agarwal'), ('Karan', 'Yadav'),
            ('Nisha', 'Mishra'), ('Aditya', 'Kumar'), ('Kavya', 'Reddy'),
            ('Manish', 'Tiwari'), ('Divya', 'Shah'), ('Sanjay', 'Nair'),
            ('Ritu', 'Malhotra'), ('Deepak', 'Bose'), ('Ananya', 'Pillai'),
            ('Tushar', 'Jain'), ('Simran', 'Kaur'),
        ]
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        student_objs = []
        for idx, (fn, ln) in enumerate(student_names):
            adm_no = f'STU2024{str(idx+1).zfill(3)}'
            email = f'{fn.lower()}.{ln.lower()}@student.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': adm_no.lower(),
                    'first_name': fn, 'last_name': ln,
                    'role': User.STUDENT, 'is_approved': True,
                    'gender': random.choice(['M', 'F']),
                }
            )
            if created:
                user.set_password('student123')
                user.save()
            student, _ = Student.objects.get_or_create(
                admission_number=adm_no,
                defaults={
                    'user': user,
                    'current_class': random.choice(class_objs),
                    'parent_name': f'Mr. {ln}',
                    'parent_phone': f'+91 98{random.randint(10000000, 99999999)}',
                    'parent_email': f'parent.{ln.lower()}@gmail.com',
                    'blood_group': random.choice(blood_groups),
                    'enrolled_date': datetime.date(2024, 6, 1),
                }
            )
            student_objs.append(student)
        self.stdout.write(f'  ✓ {len(student_objs)} students created (password: student123)')

        # ── Attendance ────────────────────────────────────────────
        from apps.attendance.models import Attendance
        today = timezone.now().date()
        statuses = ['present', 'present', 'present', 'present', 'absent', 'late']
        att_count = 0
        for student in student_objs[:10]:
            for days_ago in range(30):
                d = today - datetime.timedelta(days=days_ago)
                if d.weekday() < 6:  # Mon-Sat
                    Attendance.objects.get_or_create(
                        student=student, date=d,
                        subject=random.choice(subjects),
                        defaults={
                            'status': random.choice(statuses),
                            'marked_by': random.choice(teacher_objs),
                        }
                    )
                    att_count += 1
        self.stdout.write(f'  ✓ {att_count} attendance records created')

        # ── Exams ─────────────────────────────────────────────────
        from apps.exams.models import Exam
        exam_objs = []
        for cls in class_objs[:3]:
            for sub in list(cls.subjects.all())[:3]:
                exam, _ = Exam.objects.get_or_create(
                    name=f'Mid Term - {sub.name}',
                    academic_class=cls,
                    subject=sub,
                    defaults={
                        'exam_type': 'midterm',
                        'exam_date': today - datetime.timedelta(days=15),
                        'start_time': datetime.time(9, 0),
                        'end_time': datetime.time(12, 0),
                        'total_marks': 100,
                        'passing_marks': 35,
                        'created_by': teacher_objs[0],
                    }
                )
                exam_objs.append(exam)
        self.stdout.write(f'  ✓ {len(exam_objs)} exams created')

        # ── Results ───────────────────────────────────────────────
        from apps.results.models import Result
        result_count = 0
        for exam in exam_objs:
            students_in_class = Student.objects.filter(current_class=exam.academic_class)
            for student in students_in_class:
                marks = random.randint(20, 98)
                Result.objects.get_or_create(
                    student=student, exam=exam, subject=exam.subject,
                    defaults={
                        'marks_obtained': marks,
                        'total_marks': exam.total_marks,
                        'entered_by': teacher_objs[0],
                    }
                )
                result_count += 1
        self.stdout.write(f'  ✓ {result_count} results created')

        # ── Assignments ───────────────────────────────────────────
        from apps.assignments.models import Assignment
        assign_count = 0
        for teacher in teacher_objs[:2]:
            for cls in teacher.assigned_classes.all():
                for sub in list(cls.subjects.all())[:2]:
                    Assignment.objects.get_or_create(
                        title=f'{sub.name} Assignment - Chapter 5',
                        assigned_class=cls,
                        defaults={
                            'description': f'Complete all exercises from Chapter 5 of {sub.name}. Show all working.',
                            'subject': sub,
                            'teacher': teacher,
                            'due_date': timezone.now() + datetime.timedelta(days=7),
                            'max_marks': 20,
                        }
                    )
                    assign_count += 1
        self.stdout.write(f'  ✓ {assign_count} assignments created')

        # ── Timetable ─────────────────────────────────────────────
        from apps.timetable.models import TimeSlot, Timetable
        slots_data = [
            ('Period 1', '08:00', '08:45', 1),
            ('Period 2', '08:45', '09:30', 2),
            ('Break', '09:30', '09:45', 3),
            ('Period 3', '09:45', '10:30', 4),
            ('Period 4', '10:30', '11:15', 5),
            ('Lunch', '11:15', '11:45', 6),
            ('Period 5', '11:45', '12:30', 7),
            ('Period 6', '12:30', '13:15', 8),
        ]
        slot_objs = []
        for name, st, et, order in slots_data:
            slot, _ = TimeSlot.objects.get_or_create(
                name=name,
                defaults={
                    'start_time': datetime.time(*map(int, st.split(':'))),
                    'end_time': datetime.time(*map(int, et.split(':'))),
                    'order': order,
                }
            )
            slot_objs.append(slot)
        self.stdout.write(f'  ✓ {len(slot_objs)} time slots created')

        # ── Fee Structures ────────────────────────────────────────
        from apps.fees.models import FeeStructure, FeeRecord
        for cls in class_objs:
            structure, _ = FeeStructure.objects.get_or_create(
                name=f'Annual Fee {cls}',
                academic_class=cls,
                academic_year='2024-25',
                defaults={
                    'tuition_fee': 45000,
                    'transport_fee': 8000,
                    'library_fee': 2000,
                    'lab_fee': 3000,
                    'misc_fee': 2000,
                    'due_date': datetime.date(2024, 7, 31),
                }
            )
            # Create fee records for each student
            for student in Student.objects.filter(current_class=cls):
                FeeRecord.objects.get_or_create(
                    student=student, fee_structure=structure,
                    defaults={
                        'amount': structure.total_amount,
                        'discount': 0,
                        'status': random.choice(['paid', 'paid', 'pending', 'partial']),
                    }
                )
        self.stdout.write('  ✓ Fee structures and records created')

        # ── Notifications ─────────────────────────────────────────
        from apps.notifications.models import Notification, Announcement
        for student in student_objs[:5]:
            Notification.objects.get_or_create(
                recipient=student.user,
                title='Welcome to EduCore!',
                defaults={
                    'message': 'Your account has been approved. Welcome to the school portal!',
                    'notification_type': 'success',
                    'sender': admin_user,
                }
            )

        Announcement.objects.get_or_create(
            title='Annual Sports Day - 2024',
            defaults={
                'content': 'We are excited to announce our Annual Sports Day on December 15, 2024. All students are encouraged to participate in various sports events.',
                'audience': 'all',
                'is_pinned': True,
                'posted_by': admin_user,
            }
        )
        Announcement.objects.get_or_create(
            title='Parent-Teacher Meeting',
            defaults={
                'content': 'A Parent-Teacher meeting is scheduled for November 30, 2024. All parents are requested to attend.',
                'audience': 'all',
                'posted_by': admin_user,
            }
        )
        self.stdout.write('  ✓ Notifications and announcements created')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!\n'))
        self.stdout.write('Demo Login Credentials:')
        self.stdout.write('  Admin:   admin@school.com    / admin123')
        self.stdout.write('  Teacher: teacher@school.com  / teacher123')
        self.stdout.write('  Student: arjun.sharma@student.com / student123')
