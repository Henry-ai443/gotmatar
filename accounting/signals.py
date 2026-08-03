
# pyrefly: ignore [missing-import]
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from main_app.models import Student, NotificationStudent, NotificationStaff
from accounting.models import FeeStructure, Invoice, InvoiceItem, Payment, Payslip, Transaction



@receiver(post_save, sender=Payment)
def handle_payment_creation(sender, instance, created, **kwargs):
    if created:
        invoice = instance.invoice
        # Update invoice status
        payments = Payment.objects.filter(invoice=invoice).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
        if payments >= invoice.total_amount:
            invoice.status = Invoice.StatusChoices.PAID
        elif payments > 0:
            invoice.status = Invoice.StatusChoices.PARTIAL
        invoice.save()

        # Create Transaction
        Transaction.objects.create(
            type=Transaction.TypeChoices.FEE_PAYMENT,
            amount=instance.amount_paid,
            invoice=invoice
        )

@receiver(post_save, sender=Payslip)
def handle_payslip_status_change(sender, instance, **kwargs):
    if instance.status == Payslip.StatusChoices.PAID and instance.paid_date:
        transaction_exists = Transaction.objects.filter(payslip=instance, type=Transaction.TypeChoices.SALARY_PAYMENT).exists()
        if not transaction_exists:
            Transaction.objects.create(
                type=Transaction.TypeChoices.SALARY_PAYMENT,
                amount=instance.net_pay,
                payslip=instance
            )
            NotificationStaff.objects.create(
                staff=instance.staff,
                message=f"Your payslip for {instance.month}/{instance.year} has been marked as paid."
            )
