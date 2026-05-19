from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('pending/', views.pending_approval, name='pending'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/<int:user_id>/make-admin/', views.make_admin, name='make_admin'),
    path('users/<int:user_id>/remove-admin/', views.remove_admin, name='remove_admin'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-security/', views.verify_security, name='verify_security'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
