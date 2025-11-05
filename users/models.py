from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from datetime import timedelta
import secrets

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)

    ROLE_CHOICES = [
        ('borrower', 'Borrower'),
        ('investor', 'Investor'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    checklist = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=255,null=True, blank=True)
    last_name = models.CharField(max_length=255,null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_account_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="user",
    )

    class Meta:
        db_table = 'users'

    def __str__(self):
        return (
            "{"
            f"email: '{self.email or ''}', "
            f"first_name: '{self.first_name or ''}', "
            f"last_name: '{self.last_name or ''}', "
            "}"
        )


class UserVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    VERIFICATION_TYPE_CHOICES = [
        ('identity', 'Identity'),
        ('address', 'Address'),
        ('income', 'Income'),
    ]
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPE_CHOICES)
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    document_url = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_verifications'
    def __str__(self):
        return f"Verification: {self.user.email} - {self.verification_type}"


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'user_address'

    def __str__(self):
        return (
            "{"
            f"street_address: '{self.street_address or ''}', "
            f"city: '{self.city or ''}', "
            f"state: '{self.state or ''}', "
            f"country: '{self.country or ''}', "
            f"postal_code: '{self.postal_code or ''}'"
            "}"
        )

class UserBankDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    routing_number = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.IntegerField( null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)


    class Meta:
        db_table = 'user_bank_account'

    def __str__(self):
        return (
            "{"
            f"account_holder_name: '{self.account_holder_name or ''}', "
            "}"
        )


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Password Reset Token for {self.user.email}"
