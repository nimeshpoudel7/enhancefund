from django.db import models
from users.models import User

class Borrower(models.Model):
    class Meta:
        db_table = 'Borrower'
    borrower = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    credit_score = models.IntegerField()
    bank_statement_url = models.CharField(max_length=255)
    loan_purpose = models.CharField(max_length=255)
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
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    credit_score = models.IntegerField()
    date_recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'credit_score_history'
    def __str__(self):
        return f"Credit Score History: {self.borrower.borrower.email} - {self.credit_score}"
