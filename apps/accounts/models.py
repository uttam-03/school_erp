"""
Custom User Model
Security Rules:
  - Only superusers can create Admin accounts
  - Nobody can register as Admin via the public form
  - Only superuser can delete/deactivate other admins
  - Regular admins can manage teachers and students only
  - is_superuser flag = highest authority
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ADMIN   = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'

    ROLE_CHOICES = [
        (ADMIN,   'Admin'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other'),
    ]
    SECURITY_QUESTIONS = [
        ('pet',    "What is the name of your first pet?"),
        ('school', "What was the name of your primary school?"),
        ('mother', "What is your mother's maiden name?"),
        ('city',   "In what city were you born?"),
        ('friend', "What is the name of your childhood best friend?"),
        ('food',   "What is your favourite food?"),
    ]

    # ── Core ──────────────────────────────────────────────────────────────────
    email      = models.EmailField(_('email address'), unique=True)
    username   = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)

    # ── Profile ───────────────────────────────────────────────────────────────
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone         = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address       = models.TextField(blank=True)
    bio           = models.TextField(blank=True)

    # ── Security question for forgot-password ─────────────────────────────────
    security_question = models.CharField(max_length=20, choices=SECURITY_QUESTIONS, blank=True)
    security_answer   = models.CharField(max_length=200, blank=True)

    # ── Status ────────────────────────────────────────────────────────────────
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        tag = ' [SUPER]' if self.is_superuser else ''
        return f"{self.get_full_name()} ({self.role}){tag}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    # ── Role helpers ──────────────────────────────────────────────────────────
    @property
    def is_admin(self):
        """True for both admin role users AND superusers."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_superadmin(self):
        """True ONLY for Django superuser — highest authority."""
        return self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.TEACHER

    @property
    def is_student_role(self):
        return self.role == self.STUDENT

    def can_manage_admins(self):
        """Only superuser can manage (approve/deactivate) other admin accounts."""
        return self.is_superuser

    def can_be_deleted_by(self, requesting_user):
        """
        Rules:
        - Superuser can delete/deactivate anyone
        - Admin can delete/deactivate Teachers and Students only
        - Nobody can delete a Superuser except another Superuser
        """
        if self.is_superuser:
            return requesting_user.is_superuser
        if self.role == self.ADMIN:
            return requesting_user.is_superuser
        return requesting_user.is_admin  # Teachers/Students: any admin

    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default-avatar.png'

    def get_dashboard_url(self):
        from django.urls import reverse
        role_map = {
            self.ADMIN:   'dashboard:admin',
            self.TEACHER: 'dashboard:teacher',
            self.STUDENT: 'dashboard:student',
        }
        return reverse(role_map.get(self.role, 'dashboard:student'))
