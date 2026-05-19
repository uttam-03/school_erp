"""Fee Management Models"""

from django.db import models
from django.utils import timezone


class FeeStructure(models.Model):
    name = models.CharField(max_length=200)
    academic_class = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='fee_structures')
    academic_year = models.CharField(max_length=10)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    misc_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_structures'

    def __str__(self):
        return f"{self.name} - {self.academic_class}"

    @property
    def total_amount(self):
        return (
            self.tuition_fee + self.transport_fee +
            self.library_fee + self.lab_fee + self.misc_fee
        )


class FeeRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fee_records')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='records')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_records'

    @property
    def net_amount(self):
        return self.amount - self.discount


class FeePayment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('online', 'Online Transfer'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]

    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fee_payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(default=timezone.now)
    received_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='collected_fees'
    )
    receipt_number = models.CharField(max_length=50, unique=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Receipt #{self.receipt_number} - {self.student}"
