from django.utils import timezone
from datetime import timedelta
from main_app.models import NotificationStudent
from accounting.models import FeeStructure, Invoice, InvoiceItem

def generate_invoices_for_student(student):
    if not student.course or not student.session:
        return None

    # Check if invoice already exists
    if Invoice.objects.filter(student=student, session=student.session).exists():
        return None

    fee_structures = FeeStructure.objects.filter(course=student.course, session=student.session)
    if not fee_structures.exists():
        return None

    due_date = timezone.now().date() + timedelta(days=30)
    invoice = Invoice.objects.create(
        student=student,
        session=student.session,
        due_date=due_date,
        total_amount=0
    )
    
    total = 0
    for fs in fee_structures:
        InvoiceItem.objects.create(
            invoice=invoice,
            category=fs.category,
            amount=fs.amount
        )
        total += fs.amount
    
    invoice.total_amount = total
    invoice.save()

    NotificationStudent.objects.create(
        student=student,
        message=f"A new invoice for {total} has been generated."
    )

    return invoice
