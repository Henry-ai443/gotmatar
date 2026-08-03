from django import forms
from .models import FeeCategory, FeeStructure, SalaryStructure, Payment
from main_app.models import Staff

class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name', 'is_recurring']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 0;'})
        }

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['course', 'session', 'category', 'amount']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ['staff', 'basic_salary', 'allowances', 'effective_from']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control'}),
            'effective_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'method', 'reference_number']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class GeneratePayslipForm(forms.Form):
    staff = forms.ModelChoiceField(queryset=Staff.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    month = forms.IntegerField(min_value=1, max_value=12, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    year = forms.IntegerField(min_value=2000, max_value=2100, widget=forms.NumberInput(attrs={'class': 'form-control'}))
