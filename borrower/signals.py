from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import BorrowerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_borrower_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'borrower':
        BorrowerProfile.objects.create(user=instance)
