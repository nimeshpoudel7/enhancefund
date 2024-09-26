from users.models import User
from django.db import models
class InvestorBalance(models.Model):
    investor = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'investor_balance'
    def __str__(self):
        return f"Investor Balance: {self.investor.email} - {self.account_balance}"
