from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class BorrowerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'borrower'
        if commit:
            user.save()
        return user

class InvestorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'investor'
        if commit:
            user.save()
        return user
