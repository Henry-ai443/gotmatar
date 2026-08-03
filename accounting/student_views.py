from django.shortcuts import render, get_object_or_404
from .models import Invoice, Payment

def view_invoices(request):
    try:
        invoices = Invoice.objects.filter(student=request.user.student)
    except AttributeError:
        invoices = []
    return render(request, 'student_template/accounting/view_invoices.html', {'invoices': invoices})

def view_invoice_details(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, student=request.user.student)
    items = invoice.items.all()
    payments = invoice.payments.all()
    return render(request, 'student_template/accounting/view_invoice_details.html', {
        'invoice': invoice,
        'items': items,
        'payments': payments
    })
