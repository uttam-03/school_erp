"""Role-Based Access Middleware"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


EXEMPT_PATHS = [
    '/accounts/login/',
    '/accounts/logout/',
    '/accounts/register/',
    '/accounts/pending/',
    '/accounts/forgot-password/',
    '/accounts/verify-security/',
    '/accounts/reset-password/',
    '/static/',
    '/media/',
]


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            user = request.user

            # Skip exempt paths
            if any(path.startswith(p) for p in EXEMPT_PATHS):
                return self.get_response(request)

            # Superuser: full access always
            if user.is_superuser:
                return self.get_response(request)

            # Any non-superuser with unapproved account → pending page
            if not user.is_approved:
                return redirect('/accounts/pending/')

            # Student restricted from admin/teacher paths
            if user.is_student_role:
                BLOCKED = ['/students/manage/', '/teachers/', '/fees/manage/',
                           '/classes/manage/', '/exams/create/', '/results/create/']
                if any(path.startswith(p) for p in BLOCKED):
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect(reverse('dashboard:student'))

        return self.get_response(request)
