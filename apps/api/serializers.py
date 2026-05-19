"""REST API Serializers"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.classes.models import Class
from apps.subjects.models import Subject
from apps.attendance.models import Attendance
from apps.results.models import Result
from apps.exams.models import Exam
from apps.assignments.models import Assignment, Submission
from apps.fees.models import FeeStructure, FeeRecord, FeePayment
from apps.notifications.models import Notification, Announcement
from apps.timetable.models import Timetable, TimeSlot
from apps.materials.models import StudyMaterial

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'role', 'phone', 'is_active', 'is_approved', 'full_name',
                  'profile_image_url', 'date_joined']
        read_only_fields = ['date_joined']

    def get_full_name(self, obj): return obj.get_full_name()
    def get_profile_image_url(self, obj): return obj.get_profile_image_url()


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    current_class_name = serializers.CharField(source='current_class.__str__', read_only=True)
    attendance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'admission_number', 'current_class', 'current_class_name',
                  'parent_name', 'parent_phone', 'parent_email', 'blood_group',
                  'enrolled_date', 'is_active', 'attendance_percentage']

    def get_attendance_percentage(self, obj): return obj.get_attendance_percentage()


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'employee_id', 'qualification', 'specialization',
                  'experience_years', 'joining_date', 'is_active',
                  'assigned_classes', 'assigned_subjects']


class ClassSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'section', 'academic_year', 'room_number',
                  'max_students', 'student_count', 'subjects', 'class_teacher']

    def get_student_count(self, obj): return obj.get_student_count()


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'max_marks', 'passing_marks', 'is_elective']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'date', 'status',
                  'subject', 'subject_name', 'marked_by', 'remarks']


class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='academic_class.__str__', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_type', 'academic_class', 'class_name',
                  'subject', 'subject_name', 'exam_date', 'start_time', 'end_time',
                  'total_marks', 'passing_marks', 'instructions']


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    percentage = serializers.SerializerMethodField()
    is_pass = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ['id', 'student', 'student_name', 'exam', 'exam_name',
                  'subject', 'subject_name', 'marks_obtained', 'total_marks',
                  'grade', 'percentage', 'is_pass', 'remarks']

    def get_percentage(self, obj): return obj.percentage
    def get_is_pass(self, obj): return obj.is_pass


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='assigned_class.__str__', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'subject', 'subject_name',
                  'assigned_class', 'class_name', 'teacher', 'teacher_name',
                  'due_date', 'max_marks', 'is_overdue', 'submissions_count', 'created_at']

    def get_is_overdue(self, obj): return obj.is_overdue
    def get_submissions_count(self, obj): return obj.submissions.count()


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student', 'student_name', 'status',
                  'marks_obtained', 'remarks', 'submitted_at', 'graded_at']


class FeeStructureSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='academic_class.__str__', read_only=True)

    class Meta:
        model = FeeStructure
        fields = ['id', 'name', 'academic_class', 'class_name', 'academic_year',
                  'tuition_fee', 'transport_fee', 'library_fee', 'lab_fee',
                  'misc_fee', 'total_amount', 'due_date']

    def get_total_amount(self, obj): return str(obj.total_amount)


class FeeRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    fee_structure_name = serializers.CharField(source='fee_structure.name', read_only=True)
    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = FeeRecord
        fields = ['id', 'student', 'student_name', 'fee_structure',
                  'fee_structure_name', 'amount', 'discount', 'net_amount', 'status']

    def get_net_amount(self, obj): return str(obj.net_amount)


class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)

    class Meta:
        model = FeePayment
        fields = ['id', 'fee_record', 'student', 'student_name', 'amount_paid',
                  'payment_method', 'transaction_id', 'payment_date',
                  'receipt_number', 'remarks', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'link', 'is_read', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'audience', 'is_pinned',
                  'posted_by', 'posted_by_name', 'expires_at', 'created_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'name', 'start_time', 'end_time', 'order']


class TimetableSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    slot_name = serializers.CharField(source='time_slot.name', read_only=True)

    class Meta:
        model = Timetable
        fields = ['id', 'academic_class', 'subject', 'subject_name',
                  'teacher', 'teacher_name', 'day', 'time_slot', 'slot_name',
                  'room', 'academic_year']


class StudyMaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    uploader_name = serializers.CharField(source='uploaded_by.user.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'description', 'subject', 'subject_name',
                  'academic_class', 'material_type', 'uploader_name',
                  'external_link', 'file_url', 'download_count', 'created_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
