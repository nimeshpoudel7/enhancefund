from django.db import models
from borrower.models import BorrowerProfile


class DocumentVerification(models.Model):
    borrower = models.ForeignKey(BorrowerProfile, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification for {self.borrower.user.username}"
