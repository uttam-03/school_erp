"""School ERP - Root URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.accounts.dashboard_urls', namespace='dashboard')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('teachers/', include('apps.teachers.urls', namespace='teachers')),
    path('classes/', include('apps.classes.urls', namespace='classes')),
    path('subjects/', include('apps.subjects.urls', namespace='subjects')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('results/', include('apps.results.urls', namespace='results')),
    path('exams/', include('apps.exams.urls', namespace='exams')),
    path('assignments/', include('apps.assignments.urls', namespace='assignments')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('timetable/', include('apps.timetable.urls', namespace='timetable')),
    path('fees/', include('apps.fees.urls', namespace='fees')),
    path('materials/', include('apps.materials.urls', namespace='materials')),
    path('api/v1/', include('apps.api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'apps.accounts.views.error_404'
handler500 = 'apps.accounts.views.error_500'
handler403 = 'apps.accounts.views.error_403'
