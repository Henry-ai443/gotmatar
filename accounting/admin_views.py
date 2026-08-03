from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FeeCategory, FeeStructure, SalaryStructure, Payslip, Invoice, Payment, Transaction
from .forms import FeeCategoryForm, FeeStructureForm, SalaryStructureForm, PaymentForm, GeneratePayslipForm

def manage_fee_category(request):
    categories = FeeCategory.objects.all()
    if request.method == 'POST':
        form = FeeCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee Category added successfully.")
            return redirect('manage_fee_category')
    else:
        form = FeeCategoryForm()
    return render(request, 'hod_template/accounting/manage_fee_category.html', {'categories': categories, 'form': form, 'page_title': 'Manage Fee Categories'})

def edit_fee_category(request, category_id):
    category = get_object_or_404(FeeCategory, id=category_id)
    if request.method == 'POST':
        form = FeeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee Category updated successfully.")
            return redirect('manage_fee_category')
    else:
        form = FeeCategoryForm(instance=category)
    return render(request, 'hod_template/accounting/edit_fee_category.html', {'form': form, 'page_title': 'Edit Fee Category', 'category': category})

def delete_fee_category(request, category_id):
    category = get_object_or_404(FeeCategory, id=category_id)
    try:
        category.delete()
        messages.success(request, "Fee Category deleted successfully.")
    except Exception as e:
        messages.error(request, f"Could not delete: {e}")
    return redirect('manage_fee_category')

def manage_fee_structure(request):
    structures = FeeStructure.objects.all()
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee Structure added successfully.")
            return redirect('manage_fee_structure')
    else:
        form = FeeStructureForm()
    return render(request, 'hod_template/accounting/manage_fee_structure.html', {'structures': structures, 'form': form, 'page_title': 'Manage Fee Structures'})

def edit_fee_structure(request, structure_id):
    structure = get_object_or_404(FeeStructure, id=structure_id)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=structure)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee Structure updated successfully.")
            return redirect('manage_fee_structure')
    else:
        form = FeeStructureForm(instance=structure)
    return render(request, 'hod_template/accounting/edit_fee_structure.html', {'form': form, 'page_title': 'Edit Fee Structure', 'structure': structure})

def delete_fee_structure(request, structure_id):
    structure = get_object_or_404(FeeStructure, id=structure_id)
    try:
        structure.delete()
        messages.success(request, "Fee Structure deleted successfully.")
    except Exception as e:
        messages.error(request, f"Could not delete: {e}")
    return redirect('manage_fee_structure')

def manage_salary_structure(request):
    structures = SalaryStructure.objects.all()
    if request.method == 'POST':
        staff = request.POST.get('staff')
        # Check if staff already has a salary structure
        existing = SalaryStructure.objects.filter(staff_id=staff).first()
        if existing:
            form = SalaryStructureForm(request.POST, instance=existing)
        else:
            form = SalaryStructureForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Salary Structure saved successfully.")
            return redirect('manage_salary_structure')
    else:
        form = SalaryStructureForm()
    return render(request, 'hod_template/accounting/manage_salary_structure.html', {'structures': structures, 'form': form, 'page_title': 'Manage Salary Structures'})

def view_invoices(request):
    invoices = Invoice.objects.all()
    return render(request, 'hod_template/accounting/view_invoices.html', {'invoices': invoices, 'page_title': 'Student Invoices'})

def record_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            if hasattr(request.user, 'staff'):
                payment.received_by = request.user.staff
            payment.save()
            messages.success(request, "Payment recorded successfully.")
            return redirect('view_invoices')
    else:
        form = PaymentForm()
    return render(request, 'hod_template/accounting/record_payment.html', {'form': form, 'invoice': invoice, 'page_title': 'Record Payment'})

def manage_payslips(request):
    payslips = Payslip.objects.all()
    form = GeneratePayslipForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            staff = form.cleaned_data.get('staff')
            month = form.cleaned_data.get('month')
            year = form.cleaned_data.get('year')
            
            # Check if payslip already exists
            if Payslip.objects.filter(staff=staff, month=month, year=year).exists():
                messages.error(request, "Payslip for this staff and month/year already exists.")
            else:
                try:
                    sal_struct = SalaryStructure.objects.get(staff=staff)
                    gross = sal_struct.basic_salary + sal_struct.allowances
                    deductions = 0 # Can be added if required
                    net = gross - deductions
                    Payslip.objects.create(
                        staff=staff,
                        month=month,
                        year=year,
                        gross=gross,
                        deductions=deductions,
                        net_pay=net,
                        status=Payslip.StatusChoices.DRAFT
                    )
                    messages.success(request, "Payslip generated successfully.")
                except SalaryStructure.DoesNotExist:
                    messages.error(request, "No salary structure found for this staff.")
            return redirect('manage_payslips')

    return render(request, 'hod_template/accounting/manage_payslips.html', {'payslips': payslips, 'form': form, 'page_title': 'Manage Payslips'})

def mark_payslip_paid(request, payslip_id):
    from django.utils import timezone
    payslip = get_object_or_404(Payslip, id=payslip_id)
    payslip.status = Payslip.StatusChoices.PAID
    payslip.paid_date = timezone.now().date()
    payslip.save()
    messages.success(request, "Payslip marked as paid.")
    return redirect('manage_payslips')

def accounting_reports(request):
    from django.db.models import Sum
    total_collected = Transaction.objects.filter(type=Transaction.TypeChoices.FEE_PAYMENT).aggregate(Sum('amount'))['amount__sum'] or 0
    total_payroll = Transaction.objects.filter(type=Transaction.TypeChoices.SALARY_PAYMENT).aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_fees = Invoice.objects.filter(status__in=[Invoice.StatusChoices.UNPAID, Invoice.StatusChoices.PARTIAL, Invoice.StatusChoices.OVERDUE]).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    payments = Payment.objects.all().order_by('-payment_date')[:10]
    
    context = {
        'total_collected': total_collected,
        'total_payroll': total_payroll,
        'outstanding_fees': outstanding_fees,
        'payments': payments,
        'page_title': 'Accounting Reports'
    }
    return render(request, 'hod_template/accounting/accounting_reports.html', context)
