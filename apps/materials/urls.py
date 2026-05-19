from django.urls import path
from . import views
app_name = 'materials'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]
