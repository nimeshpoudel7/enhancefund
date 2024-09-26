from django.db import models
from users.models import User

class Staff(models.Model):
    staff = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('support', 'Support'),
        ('analyst', 'Analyst'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff'
    def __str__(self):
        return f"Staff: {self.staff.email} - {self.role}"
