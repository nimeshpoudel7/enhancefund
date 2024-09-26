from django.db import models
from users.models import User


class InvestorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)  # Extends User model
    portfolio_balance = models.DecimalField(
        max_digits=15, decimal_places=2)  # Investor's total funds
    risk_tolerance = models.CharField(max_length=50, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ])  # Investor's risk tolerance level

    def __str__(self):
        return f"Investor: {self.user.username} - Risk: {self.risk_tolerance}"
