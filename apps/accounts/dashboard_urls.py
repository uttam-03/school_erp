"""Dashboard URLs - role-based routing"""

from django.urls import path
from apps.accounts.dashboard_views import AdminDashboard, TeacherDashboard, StudentDashboard, DashboardRouter

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardRouter.as_view(), name='index'),
    path('admin/', AdminDashboard.as_view(), name='admin'),
    path('teacher/', TeacherDashboard.as_view(), name='teacher'),
    path('student/', StudentDashboard.as_view(), name='student'),
]
