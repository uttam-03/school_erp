"""
Account Views
Security Rules enforced here:
  1. Nobody can register as Admin
  2. All new users need Superuser/Admin approval (except superuser itself)
  3. Only Superuser can approve/deactivate Admin accounts
  4. Only Superuser can delete Admin accounts
  5. Regular Admin can only manage Teachers and Students
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import LoginForm, RegisterForm, ProfileUpdateForm, CustomPasswordChangeForm

User = get_user_model()


# ── Login / Logout / Register ─────────────────────────────────────────────────

class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        return render(request, self.template_name, {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Superuser always passes through
            if not user.is_superuser and not user.is_approved:
                return redirect('accounts:pending')
            login(request, user)
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save(update_fields=['last_login_ip'])
            messages.success(request, f'Welcome back, {user.get_short_name()}!')
            return redirect(request.GET.get('next', user.get_dashboard_url()))
        return render(request, self.template_name, {'form': form})


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        return render(request, self.template_name, {
            'form': RegisterForm(),
            'security_questions': User.SECURITY_QUESTIONS,
        })

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Double-check: force non-admin even if someone tampers the form
            if user.role == User.ADMIN:
                messages.error(request, 'Admin accounts cannot be created via registration.')
                return render(request, self.template_name, {
                    'form': form,
                    'security_questions': User.SECURITY_QUESTIONS,
                })
            user.security_question = request.POST.get('security_question', '')
            user.security_answer   = request.POST.get('security_answer', '').strip().lower()
            user.is_approved       = False
            user.is_staff          = False
            user.is_superuser      = False
            user.save()
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('accounts:pending')
        return render(request, self.template_name, {
            'form': form,
            'security_questions': User.SECURITY_QUESTIONS,
        })


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'Logged out successfully.')
        return redirect('accounts:login')

    def get(self, request):
        logout(request)
        return redirect('accounts:login')


# ── Forgot Password (Security Question) ──────────────────────────────────────

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user  = User.objects.filter(email=email).first()
        if user and user.security_question:
            request.session['reset_user_id'] = user.pk
            return redirect('accounts:verify_security')
        messages.error(request, 'No account found with that email, or no security question set.')
    return render(request, 'accounts/forgot_password.html')


def verify_security(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('accounts:forgot_password')
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip().lower()
        if answer == user.security_answer.strip().lower():
            request.session['reset_verified'] = True
            return redirect('accounts:reset_password')
        messages.error(request, 'Incorrect answer. Please try again.')
    question_label = dict(User.SECURITY_QUESTIONS).get(user.security_question, '')
    return render(request, 'accounts/verify_security.html', {'question': question_label})


def reset_password(request):
    if not request.session.get('reset_verified'):
        return redirect('accounts:forgot_password')
    user = get_object_or_404(User, pk=request.session.get('reset_user_id'))
    if request.method == 'POST':
        p1 = request.POST.get('password1', '')
        p2 = request.POST.get('password2', '')
        if not p1 or len(p1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif p1 != p2:
            messages.error(request, 'Passwords do not match.')
        else:
            user.set_password(p1)
            user.save()
            del request.session['reset_user_id']
            del request.session['reset_verified']
            messages.success(request, 'Password reset successfully! Please login.')
            return redirect('accounts:login')
    return render(request, 'accounts/reset_password.html')


# ── Profile ────────────────────────────────────────────────────────────────────

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        return render(request, self.template_name, {
            'password_form': CustomPasswordChangeForm(user=request.user),
            'security_questions': User.SECURITY_QUESTIONS,
        })

    def post(self, request):
        if 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                update_session_auth_hash(request, password_form.save())
                messages.success(request, 'Password changed successfully!')
                return redirect('accounts:profile')
            messages.error(request, 'Please correct the errors below.')
            return render(request, self.template_name, {
                'password_form': password_form,
                'security_questions': User.SECURITY_QUESTIONS,
                'active_tab': 'password',
            })
        elif 'update_security' in request.POST:
            request.user.security_question = request.POST.get('security_question', '')
            request.user.security_answer   = request.POST.get('security_answer', '').strip().lower()
            request.user.save(update_fields=['security_question', 'security_answer'])
            messages.success(request, 'Security question updated!')
            return redirect('accounts:profile')
        else:
            u = request.user
            u.first_name = request.POST.get('first_name', u.first_name)
            u.last_name  = request.POST.get('last_name',  u.last_name)
            u.phone      = request.POST.get('phone',      u.phone)
            u.address    = request.POST.get('address',    u.address)
            u.bio        = request.POST.get('bio',        u.bio)
            u.gender     = request.POST.get('gender',     u.gender)
            dob = request.POST.get('date_of_birth', '')
            if dob:
                u.date_of_birth = dob
            if request.FILES.get('profile_image'):
                u.profile_image = request.FILES['profile_image']
            u.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')


@login_required
def pending_approval(request):
    if request.user.is_superuser or request.user.is_approved:
        return redirect(request.user.get_dashboard_url())
    return render(request, 'accounts/pending.html')


# ── Admin User Management ──────────────────────────────────────────────────────

@login_required
def manage_users(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    search        = request.GET.get('search', '')
    role_filter   = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all()

    # Regular admin sees only Teachers & Students (not other Admins / Superusers)
    if not request.user.is_superuser:
        users = users.exclude(role=User.ADMIN).exclude(is_superuser=True)

    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)  |
            Q(email__icontains=search)
        )
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter == 'approved':
        users = users.filter(is_approved=True)
    elif status_filter == 'pending':
        users = users.filter(is_approved=False)

    paginator = Paginator(users.order_by('-date_joined'), 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_panel/users.html', {
        'page_obj':      page,
        'search':        search,
        'role_filter':   role_filter,
        'status_filter': status_filter,
        'is_superuser':  request.user.is_superuser,
    })


@login_required
def approve_user(request, user_id):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    target = get_object_or_404(User, pk=user_id)

    # Only Superuser can approve Admin accounts
    if target.role == User.ADMIN and not request.user.is_superuser:
        messages.error(request, 'Only the Superuser can approve Admin accounts.')
        return redirect('accounts:manage_users')

    # Nobody can approve another Superuser via this UI
    if target.is_superuser:
        messages.error(request, 'Superuser accounts cannot be managed here.')
        return redirect('accounts:manage_users')

    target.is_approved = True
    target.save(update_fields=['is_approved'])
    messages.success(request, f'{target.get_full_name()} approved successfully.')
    return redirect('accounts:manage_users')


@login_required
def deactivate_user(request, user_id):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())

    target = get_object_or_404(User, pk=user_id)

    # Block deactivating superusers
    if target.is_superuser:
        messages.error(request, 'Superuser accounts cannot be deactivated from here.')
        return redirect('accounts:manage_users')

    # Regular admin cannot deactivate other admins
    if target.role == User.ADMIN and not request.user.is_superuser:
        messages.error(request, 'Only the Superuser can deactivate Admin accounts.')
        return redirect('accounts:manage_users')

    # Prevent self-deactivation
    if target.pk == request.user.pk:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('accounts:manage_users')

    target.is_active = not target.is_active
    target.save(update_fields=['is_active'])
    status = 'activated' if target.is_active else 'deactivated'
    messages.success(request, f'{target.get_full_name()} has been {status}.')
    return redirect('accounts:manage_users')


@login_required
def make_admin(request, user_id):
    """Only Superuser can promote a Teacher/Student to Admin."""
    if not request.user.is_superuser:
        messages.error(request, 'Only Superuser can assign Admin role.')
        return redirect('accounts:manage_users')

    target = get_object_or_404(User, pk=user_id)
    if target.is_superuser:
        messages.error(request, 'Cannot change Superuser role.')
        return redirect('accounts:manage_users')

    target.role       = User.ADMIN
    target.is_approved = True
    target.save(update_fields=['role', 'is_approved'])
    messages.success(request, f'{target.get_full_name()} is now an Admin.')
    return redirect('accounts:manage_users')


@login_required
def remove_admin(request, user_id):
    """Only Superuser can demote an Admin back to Teacher/Student."""
    if not request.user.is_superuser:
        messages.error(request, 'Only Superuser can remove Admin role.')
        return redirect('accounts:manage_users')

    target = get_object_or_404(User, pk=user_id)
    if target.is_superuser:
        messages.error(request, 'Cannot demote a Superuser.')
        return redirect('accounts:manage_users')

    new_role = request.POST.get('new_role', User.TEACHER)
    if new_role not in (User.TEACHER, User.STUDENT):
        new_role = User.TEACHER

    target.role = new_role
    target.save(update_fields=['role'])
    messages.success(request, f'{target.get_full_name()} is now a {new_role.title()}.')
    return redirect('accounts:manage_users')


def error_404(request, exception):
    return render(request, 'shared/404.html', status=404)

def error_500(request):
    return render(request, 'shared/500.html', status=500)

def error_403(request, exception):
    return render(request, 'shared/403.html', status=403)
