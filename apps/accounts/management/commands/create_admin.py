from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
User = get_user_model()

class Command(BaseCommand):
    help = 'Create default admin user'
    def handle(self, *args, **kwargs):
        if User.objects.filter(email='admin@school.com').exists():
            self.stdout.write(self.style.WARNING('Admin already exists.'))
            return
        user = User.objects.create_superuser(
            email='admin@school.com', username='admin',
            first_name='School', last_name='Admin', password='Admin@123456'
        )
        user.is_approved = True
        user.role = User.ADMIN
        user.save()
        self.stdout.write(self.style.SUCCESS('Admin created: admin@school.com / Admin@123456'))
