from django.db import models
from borrower.models import Borrower
from users.models import User

class Loan(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    term_months = models.IntegerField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('repaid', 'Repaid'),
        ('defaulted', 'Defaulted'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    loan_purpose = models.CharField(max_length=255,null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_payable = models.DecimalField(max_digits=10, decimal_places=2)
    is_fulfill = models.BooleanField(default=False)

    loan_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loan'

    def __str__(self):
        return (
            "{"
            f"amount: '{self.amount or 0}', "
            f"term_months: '{self.term_months or ''}', "
            f"status: '{self.status or ''}', "
            f"interest_rate: '{self.interest_rate or ''}', "
            f"total_payable: '{self.total_payable or ''}', "
            f"is_fulfill: '{self.is_fulfill}', "
            f"loan_amount: '{self.loan_amount}', "

            
            
            "}")

class Investment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_return = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'investment'

    def __str__(self):
        return f"Investment: {self.amount} by {self.investor.email} in Loan {self.loan_id}"
class EMIPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'emi_payment'

    def __str__(self):
        return f"EMI Payment: {self.amount} for Loan {self.loan_id}"
class LoanApplication(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    loan_purpose = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    application_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'loan_application'

    def __str__(self):
        return f"Loan Application: {self.amount_requested} by {self.borrower.borrower.email}"
class LoanRepaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    installment_number = models.IntegerField()
    due_date = models.DateTimeField(null=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('missed', 'Missed'),
    ]
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loan_repayment_schedule'

    def __str__(self):
        return (
            "{"
            f"installment_number: '{self.installment_number or 0}', "
            f"due_date: '{self.due_date or ''}', "
            f"payment_status: '{self.payment_status or ''}', "
            f"amount_paid: '{self.amount_paid or 0}', "
            f"amount_due: '{self.amount_due or 0}', "
            "}"
        )
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    TRANSACTION_TYPE_CHOICES = [
        ('investment', 'Investment'),
        ('payment', 'Payment'),
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    payment_id=models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'transaction'

    def __str__(self):
        return (
            "{"
            f"transaction_type: '{self.transaction_type or ''}', "
            f"amount: '{self.amount or ''}', "
            f"payment_id: '{self.payment_id or ''}', "
            "}"
        )
class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    stripe_payment_id = models.CharField(max_length=255, unique=True)
    class Meta:
        db_table = 'payment_history'

    def __str__(self):
        return (
            "{"
            f"amount: '{self.payment_amount or ''}', "
            f"stripe_payment_id: '{self.stripe_payment_id or ''}', "
            f"payment_date: '{self.payment_date or ''}', "
            "}"
        )
