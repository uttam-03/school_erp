from django.urls import path
from . import views
app_name = 'assignments'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/submit/', views.submit, name='submit'),
    path('submission/<int:pk>/grade/', views.grade_submission, name='grade'),
]
