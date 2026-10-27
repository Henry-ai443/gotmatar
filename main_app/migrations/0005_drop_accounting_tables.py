# Generated manually: drop legacy accounting tables (dry migration - review before applying)
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0004_student_registration_number"),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
DROP TABLE IF EXISTS accounting_transaction;
DROP TABLE IF EXISTS accounting_payment;
DROP TABLE IF EXISTS accounting_invoiceitem;
DROP TABLE IF EXISTS accounting_feestructure;
DROP TABLE IF EXISTS accounting_invoice;
DROP TABLE IF EXISTS accounting_payslip;
DROP TABLE IF EXISTS accounting_feecategory;
DROP TABLE IF EXISTS accounting_salarystructure;
''',
            reverse_sql='''
-- Irreversible drop: recreate statements not provided. Reverse is a no-op.
''',
        ),
    ]
