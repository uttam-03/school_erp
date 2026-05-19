"""Dashboard Views with Analytics"""

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Sum
from django.utils import timezone

User = get_user_model()


@method_decorator(login_required, name='dispatch')
class DashboardRouter(View):
    """Route users to their role-specific dashboard."""

    def get(self, request):
        return redirect(request.user.get_dashboard_url())


@method_decorator(login_required, name='dispatch')
class AdminDashboard(View):
    template_name = 'admin_panel/dashboard.html'

    def get(self, request):
        if not request.user.is_admin:
            return redirect(request.user.get_dashboard_url())

        from apps.students.models import Student
        from apps.teachers.models import Teacher
        from apps.classes.models import Class
        from apps.fees.models import FeePayment
        from apps.attendance.models import Attendance
        from apps.notifications.models import Notification

        today = timezone.now().date()

        # Core stats
        stats = {
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_teachers': Teacher.objects.filter(is_active=True).count(),
            'total_classes': Class.objects.count(),
            'pending_users': User.objects.filter(is_approved=False).count(),
            'today_attendance': Attendance.objects.filter(date=today).count(),
            'total_revenue': FeePayment.objects.filter(
                payment_date__year=today.year
            ).aggregate(total=Sum('amount_paid'))['total'] or 0,
            'unread_notifications': Notification.objects.filter(
                recipient=request.user, is_read=False
            ).count(),
        }

        # Monthly attendance data for chart (last 6 months)
        from django.db.models.functions import TruncMonth
        attendance_chart = []
        for i in range(5, -1, -1):
            month = today.replace(day=1) - timezone.timedelta(days=30 * i)
            count = Attendance.objects.filter(
                date__year=month.year,
                date__month=month.month,
                status='present'
            ).count()
            attendance_chart.append({
                'month': month.strftime('%b'),
                'count': count
            })

        # Recent students
        recent_students = Student.objects.select_related(
            'user', 'current_class'
        ).order_by('-enrolled_date')[:5]

        # Recent fee payments
        recent_payments = FeePayment.objects.select_related(
            'student__user'
        ).order_by('-payment_date')[:5]

        # Gender distribution
        gender_dist = Student.objects.values(
            'user__gender'
        ).annotate(count=Count('id'))

        # Pending approvals
        pending_approvals = User.objects.filter(
            is_approved=False
        ).order_by('-date_joined')[:5]

        return render(request, self.template_name, {
            'stats': stats,
            'attendance_chart': attendance_chart,
            'recent_students': recent_students,
            'recent_payments': recent_payments,
            'gender_dist': list(gender_dist),
            'pending_approvals': pending_approvals,
            'page_title': 'Admin Dashboard',
        })


@method_decorator(login_required, name='dispatch')
class TeacherDashboard(View):
    template_name = 'teachers/dashboard.html'

    def get(self, request):
        if not request.user.is_teacher:
            return redirect(request.user.get_dashboard_url())

        from apps.teachers.models import Teacher
        from apps.attendance.models import Attendance
        from apps.assignments.models import Assignment
        from apps.classes.models import Class

        today = timezone.now().date()
        teacher = Teacher.objects.filter(user=request.user).first()

        stats = {}
        assigned_classes = []
        recent_assignments = []
        today_attendance = []

        if teacher:
            assigned_classes = teacher.assigned_classes.all()
            student_count = sum(c.students.count() for c in assigned_classes)

            stats = {
                'assigned_classes': assigned_classes.count(),
                'total_students': student_count,
                'assignments_given': Assignment.objects.filter(teacher=teacher).count(),
                'today_attendance': Attendance.objects.filter(
                    date=today, marked_by=teacher
                ).count(),
            }

            recent_assignments = Assignment.objects.filter(
                teacher=teacher
            ).order_by('-created_at')[:5]

            today_attendance = Attendance.objects.filter(
                date=today, marked_by=teacher
            ).select_related('student__user')[:10]

        return render(request, self.template_name, {
            'teacher': teacher,
            'stats': stats,
            'assigned_classes': assigned_classes,
            'recent_assignments': recent_assignments,
            'today_attendance': today_attendance,
            'page_title': 'Teacher Dashboard',
        })


@method_decorator(login_required, name='dispatch')
class StudentDashboard(View):
    template_name = 'students/dashboard.html'

    def get(self, request):
        if not request.user.is_student_role:
            return redirect(request.user.get_dashboard_url())

        from apps.students.models import Student
        from apps.attendance.models import Attendance
        from apps.results.models import Result
        from apps.assignments.models import Assignment, Submission
        from apps.fees.models import FeeRecord

        student = Student.objects.filter(user=request.user).first()

        stats = {}
        recent_results = []
        pending_assignments = []
        attendance_pct = 0

        if student:
            total_att = Attendance.objects.filter(student=student).count()
            present_att = Attendance.objects.filter(student=student, status='present').count()
            attendance_pct = round((present_att / total_att * 100), 1) if total_att else 0

            from apps.fees.models import FeePayment as FP
            total_fee = FeeRecord.objects.filter(student=student).aggregate(t=Sum('amount'))['t'] or 0
            total_paid_amt = FP.objects.filter(student=student).aggregate(t=Sum('amount_paid'))['t'] or 0
            pending_fees_amt = max(0, float(total_fee) - float(total_paid_amt))
            stats = {
                'attendance_pct': attendance_pct,
                'total_subjects': student.current_class.subjects.count() if student.current_class else 0,
                'pending_fees': pending_fees_amt,
                'total_fee': total_fee,
                'total_paid': total_paid_amt,
                'assignments_pending': Assignment.objects.filter(
                    assigned_class=student.current_class
                ).exclude(
                    submissions__student=student
                ).count() if student.current_class else 0,
            }

            recent_results = Result.objects.filter(
                student=student
            ).select_related('exam', 'subject').order_by('-created_at')[:5]

            pending_assignments = Assignment.objects.filter(
                assigned_class=student.current_class
            ).exclude(
                submissions__student=student
            ).order_by('due_date')[:5] if student.current_class else []

        # Attendance chart data
        from django.db.models import Count as DjCount
        att_data = Attendance.objects.filter(student=student).values(
            'status'
        ).annotate(count=DjCount('id')) if student else []

        return render(request, self.template_name, {
            'student': student,
            'stats': stats,
            'recent_results': recent_results,
            'pending_assignments': pending_assignments,
            'attendance_pct': attendance_pct,
            'att_data': list(att_data),
            'page_title': 'Student Dashboard',
        })
