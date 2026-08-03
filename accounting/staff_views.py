from django.shortcuts import render
from .models import SalaryStructure, Payslip

def view_salary_structure(request):
    try:
        structure = SalaryStructure.objects.get(staff=request.user.staff)
    except (SalaryStructure.DoesNotExist, AttributeError):
        structure = None
    return render(request, 'staff_template/accounting/view_salary_structure.html', {'structure': structure})

def view_payslips(request):
    try:
        payslips = Payslip.objects.filter(staff=request.user.staff)
    except AttributeError:
        payslips = []
    return render(request, 'staff_template/accounting/view_payslips.html', {'payslips': payslips})
