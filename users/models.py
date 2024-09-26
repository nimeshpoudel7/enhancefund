# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('borrower', 'Borrower'),
        ('investor', 'Investor'),
        ('staff', 'Staff'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='borrower')

    def __str__(self):
        return self.username
