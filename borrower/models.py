from django.db import models
from django.conf import settings

class BorrowerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    credit_score = models.IntegerField()
    loan_purpose = models.TextField()

    def __str__(self):
        return f"Borrower: {self.user.username} - Credit Score: {self.credit_score}"
