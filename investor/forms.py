from django import forms
from .models import InvestorProfile


class InvestorProfileForm(forms.ModelForm):
    class Meta:
        model = InvestorProfile
        fields = ['portfolio_balance', 'risk_tolerance']

    def save(self, commit=True):
        investor = super().save(commit=False)
        if commit:
            investor.save()
        return investor
