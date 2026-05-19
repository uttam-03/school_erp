"""Fee Management Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
import uuid

from .models import FeeStructure, FeeRecord, FeePayment
from apps.students.models import Student
from apps.classes.models import Class


@login_required
def index(request):
    user = request.user
    if user.is_student_role:
        student = get_object_or_404(Student, user=user)
        records = FeeRecord.objects.filter(student=student).select_related('fee_structure').order_by('-created_at')
        payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
        total_fee = records.aggregate(t=Sum('amount'))['t'] or 0
        total_paid = payments.aggregate(t=Sum('amount_paid'))['t'] or 0
        total_pending = max(0, total_fee - total_paid)
        return render(request, 'fees/student_fees.html', {
            'records': records, 'payments': payments,
            'total_fee': total_fee, 'total_paid': total_paid,
            'total_pending': total_pending, 'student': student,
            'page_title': 'My Fees',
        })
    if not user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(user.get_dashboard_url())

    structures = FeeStructure.objects.select_related('academic_class').order_by('-created_at')
    recent_payments = FeePayment.objects.select_related('student__user').order_by('-payment_date')[:20]
    total_collected = FeePayment.objects.aggregate(t=Sum('amount_paid'))['t'] or 0
    total_pending = FeeRecord.objects.filter(status='pending').aggregate(t=Sum('amount'))['t'] or 0

    return render(request, 'fees/index.html', {
        'structures': structures, 'recent_payments': recent_payments,
        'total_collected': total_collected, 'total_pending': total_pending,
        'page_title': 'Fee Management',
    })


@login_required
def create(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    classes = Class.objects.all()
    if request.method == 'POST':
        FeeStructure.objects.create(
            name=request.POST.get('name'),
            academic_class_id=request.POST.get('academic_class'),
            academic_year=request.POST.get('academic_year'),
            tuition_fee=request.POST.get('tuition_fee', 0) or 0,
            transport_fee=request.POST.get('transport_fee', 0) or 0,
            library_fee=request.POST.get('library_fee', 0) or 0,
            lab_fee=request.POST.get('lab_fee', 0) or 0,
            misc_fee=request.POST.get('misc_fee', 0) or 0,
            due_date=request.POST.get('due_date'),
        )
        messages.success(request, 'Fee structure created.')
        return redirect('fees:index')
    return render(request, 'fees/form.html', {
        'classes': classes, 'page_title': 'New Fee Structure', 'action': 'create'
    })


@login_required
def detail(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)
    records = FeeRecord.objects.filter(fee_structure=structure).select_related('student__user')
    return render(request, 'fees/detail.html', {
        'structure': structure, 'records': records, 'page_title': structure.name,
    })


@login_required
def edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    structure = get_object_or_404(FeeStructure, pk=pk)
    classes = Class.objects.all()
    if request.method == 'POST':
        structure.name = request.POST.get('name', structure.name)
        structure.tuition_fee = request.POST.get('tuition_fee', structure.tuition_fee)
        structure.transport_fee = request.POST.get('transport_fee', structure.transport_fee)
        structure.library_fee = request.POST.get('library_fee', structure.library_fee)
        structure.lab_fee = request.POST.get('lab_fee', structure.lab_fee)
        structure.misc_fee = request.POST.get('misc_fee', structure.misc_fee)
        structure.due_date = request.POST.get('due_date', structure.due_date)
        structure.save()
        messages.success(request, 'Fee structure updated.')
        return redirect('fees:index')
    return render(request, 'fees/form.html', {
        'structure': structure, 'classes': classes,
        'page_title': 'Edit Fee Structure', 'action': 'edit',
    })


@login_required
def delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    get_object_or_404(FeeStructure, pk=pk).delete()
    messages.success(request, 'Fee structure deleted.')
    return redirect('fees:index')


@login_required
def collect_payment(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect(request.user.get_dashboard_url())
    students = Student.objects.filter(is_active=True).select_related('user')
    if request.method == 'POST':
        record_id = request.POST.get('fee_record')
        record = get_object_or_404(FeeRecord, pk=record_id)
        amount = float(request.POST.get('amount_paid', 0) or 0)
        payment = FeePayment.objects.create(
            fee_record=record,
            student=record.student,
            amount_paid=amount,
            payment_method=request.POST.get('payment_method', 'cash'),
            transaction_id=request.POST.get('transaction_id', ''),
            payment_date=request.POST.get('payment_date') or timezone.now().date(),
            received_by=request.user,
            receipt_number=f"RCP-{uuid.uuid4().hex[:8].upper()}",
            remarks=request.POST.get('remarks', ''),
        )
        total_paid = record.payments.aggregate(t=Sum('amount_paid'))['t'] or 0
        if total_paid >= record.net_amount:
            record.status = 'paid'
        elif total_paid > 0:
            record.status = 'partial'
        record.save()
        messages.success(request, f'Payment of ₹{amount} recorded. Receipt: {payment.receipt_number}')
        return redirect('fees:index')
    return render(request, 'fees/collect.html', {
        'students': students, 'page_title': 'Collect Payment'
    })


@login_required
def fee_slip(request, payment_id):
    """Generate printable fee slip for a payment."""
    payment = get_object_or_404(FeePayment, pk=payment_id)
    # Allow student to see own slip, admin sees all
    if request.user.is_student_role:
        student = get_object_or_404(Student, user=request.user)
        if payment.student != student:
            messages.error(request, 'Access denied.')
            return redirect('fees:index')
    return render(request, 'fees/fee_slip.html', {
        'payment': payment,
        'student': payment.student,
        'page_title': f'Fee Slip - {payment.receipt_number}',
    })


@login_required
def student_fee_detail(request):
    """Student: detailed fee + slip view."""
    if not request.user.is_student_role:
        return redirect('fees:index')
    student = get_object_or_404(Student, user=request.user)
    records = FeeRecord.objects.filter(student=student).select_related('fee_structure')
    payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    total_fee = records.aggregate(t=Sum('amount'))['t'] or 0
    total_paid = payments.aggregate(t=Sum('amount_paid'))['t'] or 0
    return render(request, 'fees/student_fees.html', {
        'records': records, 'payments': payments,
        'total_fee': total_fee, 'total_paid': total_paid,
        'total_pending': max(0, total_fee - total_paid),
        'student': student, 'page_title': 'My Fees',
    })


@login_required
def student_pay(request, record_id):
    """Student self-pays a pending fee record via UPI/online."""
    if not request.user.is_student_role:
        messages.error(request, 'Access denied.')
        return redirect('fees:index')

    student = get_object_or_404(Student, user=request.user)
    record = get_object_or_404(FeeRecord, pk=record_id, student=student)

    if record.status == 'paid':
        messages.info(request, 'This fee is already paid.')
        return redirect('fees:index')

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'upi')
        txn_id = request.POST.get('transaction_id', '').strip()
        amount = request.POST.get('amount_paid', '').strip()

        # Validate
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid amount.')
            return render(request, 'fees/student_pay.html', {
                'record': record, 'student': student
            })

        if method in ('upi', 'online') and not txn_id:
            messages.error(request, 'Transaction ID is required for UPI / Online payments.')
            return render(request, 'fees/student_pay.html', {
                'record': record, 'student': student
            })

        payment = FeePayment.objects.create(
            fee_record=record,
            student=student,
            amount_paid=amount,
            payment_method=method,
            transaction_id=txn_id,
            payment_date=timezone.now().date(),
            received_by=None,          # self-payment
            receipt_number=f"SELF-{uuid.uuid4().hex[:8].upper()}",
            remarks=f"Self payment by student via {method}",
        )

        # Update record status
        total_paid = record.payments.aggregate(t=Sum('amount_paid'))['t'] or 0
        if total_paid >= record.net_amount:
            record.status = 'paid'
        else:
            record.status = 'partial'
        record.save()

        messages.success(
            request,
            f'✅ Payment of ₹{amount:.0f} recorded! Receipt No: {payment.receipt_number}'
        )
        return redirect('fees:slip', payment_id=payment.pk)

    return render(request, 'fees/student_pay.html', {
        'record': record,
        'student': student,
        'page_title': 'Pay Fee',
    })
