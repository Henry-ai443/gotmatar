from django.urls import path
from . import admin_views, staff_views, student_views

urlpatterns = [
    # Admin
    path('admin/fee-category/', admin_views.manage_fee_category, name='manage_fee_category'),
    path('admin/fee-category/edit/<int:category_id>/', admin_views.edit_fee_category, name='edit_fee_category'),
    path('admin/fee-category/delete/<int:category_id>/', admin_views.delete_fee_category, name='delete_fee_category'),
    
    path('admin/fee-structure/', admin_views.manage_fee_structure, name='manage_fee_structure'),
    path('admin/fee-structure/edit/<int:structure_id>/', admin_views.edit_fee_structure, name='edit_fee_structure'),
    path('admin/fee-structure/delete/<int:structure_id>/', admin_views.delete_fee_structure, name='delete_fee_structure'),
    
    path('admin/salary-structure/', admin_views.manage_salary_structure, name='manage_salary_structure'),
    
    path('admin/invoices/', admin_views.view_invoices, name='view_invoices'),
    path('admin/invoice/<int:invoice_id>/pay/', admin_views.record_payment, name='record_payment'),
    
    path('admin/payslips/', admin_views.manage_payslips, name='manage_payslips'),
    path('admin/payslips/mark-paid/<int:payslip_id>/', admin_views.mark_payslip_paid, name='mark_payslip_paid'),
    
    path('admin/reports/', admin_views.accounting_reports, name='accounting_reports'),

    # Staff
    path('staff/salary-structure/', staff_views.view_salary_structure, name='staff_view_salary_structure'),
    path('staff/payslips/', staff_views.view_payslips, name='staff_view_payslips'),

    # Student
    path('student/invoices/', student_views.view_invoices, name='student_view_invoices'),
    path('student/invoice/<int:invoice_id>/', student_views.view_invoice_details, name='student_view_invoice_details'),
]
