from django.shortcuts import render
from django.db.models import Sum, F, Count, Q, DecimalField, Value
from django.db.models.functions import Coalesce
from .models import Transaction, Invoice, Payment, Staff
from main_app.models import CustomUser

def accountant_home(request):
    """Dashboard for Accountant role.
    Shows financial summaries and recent payments.
    """
    # Total fees collected (sum of fee_payment transactions)
    total_collected = Transaction.objects.filter(type='fee_payment').aggregate(total=Sum('amount'))['total'] or 0

    # Total outstanding fees: sum of invoice total_amount minus sum of related payments
    # Calculate paid amount per invoice via related payments
    invoices = Invoice.objects.all()
    paid_agg = invoices.annotate(
        paid=Coalesce(Sum('payments__amount_paid'), Value(0), output_field=DecimalField())
    ).aggregate(
        outstanding=Sum(F('total_amount') - F('paid'), output_field=DecimalField())
    )
    total_outstanding = paid_agg['outstanding'] or 0

    # Count of invoices by status
    invoice_counts = Invoice.objects.values('status').annotate(cnt=Count('id'))
    status_counts = {item['status']: item['cnt'] for item in invoice_counts}

    # Recent payments (5 most recent)
    recent_payments_qs = Payment.objects.select_related('invoice__student__admin').order_by('-payment_date')[:5]
    recent_payments = []
    for p in recent_payments_qs:
        student = p.invoice.student.admin
        recent_payments.append({
            'student_name': f"{student.last_name}, {student.first_name}",
            'amount': p.amount_paid,
            'date': p.payment_date,
            'method': p.method,
        })

    context = {
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'status_counts': status_counts,
        'recent_payments': recent_payments,
        'page_title': 'Accountant Dashboard',
    }
    return render(request, 'accountant/accountant_home.html', context)
