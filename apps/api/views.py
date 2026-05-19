"""REST API Views"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Sum

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

from .serializers import (
    UserSerializer, StudentSerializer, TeacherSerializer, ClassSerializer,
    SubjectSerializer, AttendanceSerializer, ResultSerializer, ExamSerializer,
    AssignmentSerializer, SubmissionSerializer, FeeStructureSerializer,
    FeeRecordSerializer, FeePaymentSerializer, NotificationSerializer,
    AnnouncementSerializer, TimetableSerializer, TimeSlotSerializer,
    StudyMaterialSerializer,
)

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_teacher
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'current_class').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['current_class', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'admission_number']

    def get_queryset(self):
        user = self.request.user
        if user.is_student_role:
            return Student.objects.filter(user=user)
        return Student.objects.select_related('user', 'current_class').all()


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user').all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['academic_year']
    search_fields = ['name', 'section']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'code']


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student__user', 'subject').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['date', 'status', 'subject']

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('student__user', 'subject')
        if user.is_student_role:
            student = Student.objects.filter(user=user).first()
            return qs.filter(student=student) if student else qs.none()
        if user.is_teacher:
            teacher = Teacher.objects.filter(user=user).first()
            return qs.filter(marked_by=teacher) if teacher else qs.none()
        return qs


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('academic_class', 'subject').all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['academic_class', 'subject', 'exam_type']

    def get_queryset(self):
        user = self.request.user
        qs = Exam.objects.select_related('academic_class', 'subject')
        if user.is_student_role:
            student = Student.objects.filter(user=user).first()
            if student and student.current_class:
                return qs.filter(academic_class=student.current_class)
            return qs.none()
        return qs


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.select_related('student__user', 'exam', 'subject').all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'exam', 'subject', 'grade']

    def get_queryset(self):
        user = self.request.user
        qs = Result.objects.select_related('student__user', 'exam', 'subject')
        if user.is_student_role:
            student = Student.objects.filter(user=user).first()
            return qs.filter(student=student) if student else qs.none()
        return qs


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('subject', 'assigned_class', 'teacher__user').all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['assigned_class', 'subject']

    def get_queryset(self):
        user = self.request.user
        qs = Assignment.objects.select_related('subject', 'assigned_class', 'teacher__user')
        if user.is_student_role:
            student = Student.objects.filter(user=user).first()
            if student and student.current_class:
                return qs.filter(assigned_class=student.current_class)
            return qs.none()
        if user.is_teacher:
            teacher = Teacher.objects.filter(user=user).first()
            return qs.filter(teacher=teacher) if teacher else qs.none()
        return qs


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('academic_class').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAdminOrReadOnly]


class FeeRecordViewSet(viewsets.ModelViewSet):
    queryset = FeeRecord.objects.select_related('student__user', 'fee_structure').all()
    serializer_class = FeeRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status']

    def get_queryset(self):
        user = self.request.user
        qs = FeeRecord.objects.select_related('student__user', 'fee_structure')
        if user.is_student_role:
            student = Student.objects.filter(user=user).first()
            return qs.filter(student=student) if student else qs.none()
        return qs


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.select_related('student__user').all()
    serializer_class = FeePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'payment_method']


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked read'})


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Announcement.objects.all()
        if user.is_student_role:
            qs = qs.filter(audience__in=['all', 'students'])
        elif user.is_teacher:
            qs = qs.filter(audience__in=['all', 'teachers'])
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.select_related('academic_class', 'subject', 'teacher__user', 'time_slot').all()
    serializer_class = TimetableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['academic_class', 'day']


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAdminOrReadOnly]


class StudyMaterialViewSet(viewsets.ModelViewSet):
    queryset = StudyMaterial.objects.select_related('subject', 'academic_class', 'uploaded_by__user').all()
    serializer_class = StudyMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['subject', 'academic_class', 'material_type']

    def get_queryset(self):
        user = self.request.user
        qs = StudyMaterial.objects.select_related('subject', 'academic_class', 'uploaded_by__user')
        if user.is_student_role:
            student = Student.objects.filter(user=user).first()
            if student and student.current_class:
                return qs.filter(academic_class=student.current_class)
            return qs.none()
        if user.is_teacher:
            teacher = Teacher.objects.filter(user=user).first()
            return qs.filter(uploaded_by=teacher) if teacher else qs.none()
        return qs


class DashboardStatsAPIView(APIView):
    """Aggregated stats for dashboard charts."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_admin:
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)

        data = {
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_teachers': Teacher.objects.filter(is_active=True).count(),
            'total_classes': Class.objects.count(),
            'pending_approvals': User.objects.filter(is_approved=False).count(),
            'total_revenue': str(FeePayment.objects.aggregate(t=Sum('amount_paid'))['t'] or 0),
            'attendance_today': Attendance.objects.filter(date=__import__('datetime').date.today()).count(),
        }
        return Response(data)
