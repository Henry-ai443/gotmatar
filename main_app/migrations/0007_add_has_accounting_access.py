"""
Generated migration to add has_accounting_access to Staff.
Do NOT apply this migration automatically; it's provided for review.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_student_date_of_birth_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='has_accounting_access',
            field=models.BooleanField(default=False),
        ),
    ]
