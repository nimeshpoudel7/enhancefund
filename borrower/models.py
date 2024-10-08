from django.db import models
from users.models import User


class Borrower(models.Model):
    class Meta:
        db_table = 'Borrower'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    EMPLOYMENT_CHOICES = [
        ('employed', 'Employed'),
        ('self-employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
    ]
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Borrower: {self.borrower.email}"


class CreditScoreHistory(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, null=True, blank=True)
    risk_score = models.IntegerField()
    average_transaction = models.FloatField()
    credit_utilization = models.FloatField()
    payment_consistency = models.FloatField(blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True)
    statement_start_date = models.DateTimeField(null=True, blank=True)
    statement_end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'credit_score_history'

    def __str__(self):
        return ("{"
                f"risk_score: '{self.risk_score or 100}', "
                f"average_transaction: '{self.average_transaction or 100}', "
                f"credit_utilization: '{self.credit_utilization or 100}', "
                f"statement_start_date: '{self.statement_start_date or ''}', "
                f"statement_end_date: '{self.statement_end_date or ''}', "

                "}")
