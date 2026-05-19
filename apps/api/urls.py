"""REST API URL Configuration"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'teachers', views.TeacherViewSet, basename='teacher')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'exams', views.ExamViewSet, basename='exam')
router.register(r'results', views.ResultViewSet, basename='result')
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')
router.register(r'submissions', views.SubmissionViewSet, basename='submission')
router.register(r'fee-structures', views.FeeStructureViewSet, basename='fee-structure')
router.register(r'fee-records', views.FeeRecordViewSet, basename='fee-record')
router.register(r'fee-payments', views.FeePaymentViewSet, basename='fee-payment')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'timetable', views.TimetableViewSet, basename='timetable')
router.register(r'time-slots', views.TimeSlotViewSet, basename='time-slot')
router.register(r'materials', views.StudyMaterialViewSet, basename='material')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token, name='api_token'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('dashboard/stats/', views.DashboardStatsAPIView.as_view(), name='dashboard_stats'),
]
