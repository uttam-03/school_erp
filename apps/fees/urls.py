from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('collect/', views.collect_payment, name='collect'),
    path('slip/<int:payment_id>/', views.fee_slip, name='slip'),
    path('my-fees/', views.student_fee_detail, name='my_fees'),
    path('pay/<int:record_id>/', views.student_pay, name='student_pay'),
]
