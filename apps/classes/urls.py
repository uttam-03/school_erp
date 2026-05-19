from django.urls import path
from . import views
app_name = 'classes'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]
