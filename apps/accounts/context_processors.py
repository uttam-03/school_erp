"""Global context processors for templates."""

from apps.notifications.models import Notification


def user_context(request):
    """Inject user-related context into all templates."""
    context = {}
    if request.user.is_authenticated:
        context['current_user'] = request.user
        context['user_role'] = request.user.role
        context['is_admin'] = request.user.is_admin
        context['is_teacher'] = request.user.is_teacher
        context['is_student'] = request.user.is_student_role
    return context
