"""Notification Views"""

from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from .models import Notification, Announcement
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def push_notification(user, title, message, notification_type='info', link=''):
    """Utility: Create DB notification and push via WebSocket."""
    notif = Notification.objects.create(
        recipient=user, title=title, message=message,
        notification_type=notification_type, link=link
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'notification_message',
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'link': link,
            'created_at': notif.created_at.isoformat(),
        }
    )
    return notif


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'shared/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'shared/announcements.html'
    context_object_name = 'announcements'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Announcement.objects.all()
        if user.is_student_role:
            qs = qs.filter(audience__in=['all', 'students'])
        elif user.is_teacher:
            qs = qs.filter(audience__in=['all', 'teachers'])
        return qs


class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    model = Announcement
    template_name = 'shared/announcement_form.html'
    fields = ['title', 'content', 'audience', 'attachment', 'is_pinned', 'expires_at']
    success_url = reverse_lazy('notifications:announcements')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, 'Announcement posted successfully.')
        return super().form_valid(form)
