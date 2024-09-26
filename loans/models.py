from django.db import models
from django.conf import settings  # To reference the AUTH_USER_MODEL


class LoanRequest(models.Model):
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the user model
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # Loan duration in months
    purpose = models.TextField()  # Purpose of the loan
    # File upload for income proof
    income_proof = models.FileField(upload_to='income_proofs/')

    def __str__(self):
        return f"Loan request by {self.borrower.username} for {self.amount}"
