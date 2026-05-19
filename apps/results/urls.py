from django.urls import path
from . import views
app_name = 'results'
urlpatterns = [
    path('', views.index, name='index'),
    path('enter/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]
