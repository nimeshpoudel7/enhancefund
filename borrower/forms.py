from django import forms
from .models import BorrowerProfile  # Ensure the correct import


class BorrowerProfileForm(forms.ModelForm):
    class Meta:
        model = BorrowerProfile
        # Include relevant fields from the model
        fields = ['income', 'credit_score', 'loan_purpose']
