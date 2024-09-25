# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('STAFF', 'Staff'),
        ('BORROWER', 'Borrower'),
        ('INVESTOR', 'Investor'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)