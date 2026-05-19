"""Notifications context processor"""

from .models import Notification


def notifications_context(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).order_by('-created_at')[:10]
        return {
            'unread_notifications': unread,
            'unread_count': unread.count(),
        }
    return {'unread_notifications': [], 'unread_count': 0}
