from django.contrib import admin
from .models import FeeStructure, FeeRecord, FeePayment

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'academic_class', 'academic_year', 'total_amount', 'due_date']

@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'amount', 'discount', 'status']
    list_filter = ['status']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'amount_paid', 'payment_method', 'payment_date']
    search_fields = ['receipt_number', 'student__user__first_name']
    date_hierarchy = 'payment_date'
