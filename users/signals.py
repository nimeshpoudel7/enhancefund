from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from users.models import Notification, User
from loans.models import Transaction, Investment, Loan
from investor.models import InvestorBalance
from users.serializers import NotificationSerializer


def send_notification_websocket(user_id, notification_data):
    """Send notification via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )
            
            # Also send unread count update
            unread_count = Notification.objects.filter(user_id=user_id, is_read=False).count()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    'type': 'unread_count_update',
                    'unread_count': unread_count
                }
            )
    except Exception as e:
        print(f"Error sending WebSocket notification: {str(e)}")


def create_notification(user, notification_type, title, message, related_id=None, related_type=None):
    """Helper function to create notifications and send via WebSocket"""
    try:
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_id=related_id,
            related_type=related_type
        )
        
        # Serialize notification for WebSocket
        serializer = NotificationSerializer(notification)
        notification_data = serializer.data
        
        # Send via WebSocket
        send_notification_websocket(user.id, notification_data)
        
        return notification
    except Exception as e:
        print(f"Error creating notification: {str(e)}")
        return None


# Signal for Fund Added (Deposit Transaction)
@receiver(post_save, sender=Transaction)
def notify_fund_added(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'deposit' and instance.payment_id != 'internal':
        user = instance.user
        create_notification(
            user=user,
            notification_type='fund_added',
            title='Fund Added Successfully',
            message=f'Your wallet has been credited with ${instance.amount:.2f}. Your new balance is available in your wallet.',
            related_id=instance.id,
            related_type='transaction'
        )


# Signal for Fund Withdrawn
@receiver(post_save, sender=Transaction)
def notify_fund_withdrawn(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'withdrawal':
        user = instance.user
        try:
            if user.role == 'investor':
                balance = InvestorBalance.objects.get(user=user)
            else:
                from borrower.models import Borrower
                balance = Borrower.objects.get(user=user)
            
            create_notification(
                user=user,
                notification_type='fund_withdrawn',
                title='Withdrawal Request Processed',
                message=f'Your withdrawal request of ${instance.amount:.2f} has been processed. Remaining balance: ${balance.account_balance:.2f}',
                related_id=instance.id,
                related_type='transaction'
            )
        except Exception as e:
            print(f"Error in withdrawal notification: {str(e)}")


# Signal for Investment Made
@receiver(post_save, sender=Investment)
def notify_investment_made(sender, instance, created, **kwargs):
    if created:
        user = instance.investor
        loan = instance.loan
        
        create_notification(
            user=user,
            notification_type='investment_made',
            title='Investment Successful',
            message=f'You have successfully invested ${instance.amount:.2f} in a loan for {loan.loan_purpose or "loan"}. Expected return will be available upon loan completion.',
            related_id=instance.id,
            related_type='investment'
        )


# Signal for Investment Return (when investment is closed)
@receiver(pre_save, sender=Investment)
def notify_investment_return(sender, instance, **kwargs):
    if instance.pk:  # Only for existing instances (updates)
        try:
            old_instance = Investment.objects.get(pk=instance.pk)
            # Check if investment status changed to closed or net_return was added
            if (old_instance.status != 'closed' and instance.status == 'closed') or \
               (old_instance.net_return is None and instance.net_return is not None and instance.net_return > 0):
                user = instance.investor
                loan = instance.loan
                
                create_notification(
                    user=user,
                    notification_type='investment_return',
                    title='Investment Return Received',
                    message=f'Congratulations! Your investment of ${instance.amount:.2f} in the loan has been completed. You received ${instance.net_return:.2f} in returns.',
                    related_id=instance.id,
                    related_type='investment'
                )
        except Investment.DoesNotExist:
            pass


# Signal for Loan Funded (notify borrower when investment is made)
@receiver(post_save, sender=Investment)
def notify_loan_funded(sender, instance, created, **kwargs):
    if created:
        loan = instance.loan
        borrower = loan.borrower.user
        
        # Calculate total funded amount
        total_funded = Investment.objects.filter(loan=loan).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        remaining = loan.amount - total_funded
        
        create_notification(
            user=borrower,
            notification_type='loan_funded',
            title='Loan Funding Update',
            message=f'Your loan request has received ${instance.amount:.2f} in funding. Total funded: ${total_funded:.2f} / ${loan.amount:.2f}. Remaining: ${remaining:.2f}',
            related_id=loan.id,
            related_type='loan'
        )


# Signal for Loan Fulfilled
@receiver(pre_save, sender=Loan)
def notify_loan_fulfilled(sender, instance, **kwargs):
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Loan.objects.get(pk=instance.pk)
            # Check if loan fulfillment status changed
            if not old_instance.is_fulfill and instance.is_fulfill:
                borrower = instance.borrower.user
                
                create_notification(
                    user=borrower,
                    notification_type='loan_fulfilled',
                    title='Loan Fully Funded!',
                    message=f'Great news! Your loan request of ${instance.amount:.2f} has been fully funded. The funds will be transferred to your account shortly.',
                    related_id=instance.id,
                    related_type='loan'
                )
                
                # Also notify all investors who invested in this loan
                investments = Investment.objects.filter(loan=instance)
                for investment in investments:
                    create_notification(
                        user=investment.investor,
                        notification_type='loan_fulfilled',
                        title='Loan Fully Funded',
                        message=f'The loan you invested ${investment.amount:.2f} in has been fully funded and approved. Repayment schedule will begin soon.',
                        related_id=instance.id,
                        related_type='loan'
                    )
        except Loan.DoesNotExist:
            pass


# Signal for Loan Approved
@receiver(pre_save, sender=Loan)
def notify_loan_approved(sender, instance, **kwargs):
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Loan.objects.get(pk=instance.pk)
            # Check if loan status changed to approved
            if old_instance.status != 'approved' and instance.status == 'approved':
                borrower = instance.borrower.user
                
                create_notification(
                    user=borrower,
                    notification_type='loan_approved',
                    title='Loan Approved!',
                    message=f'Congratulations! Your loan application of ${instance.amount:.2f} has been approved. Funds will be available in your account.',
                    related_id=instance.id,
                    related_type='loan'
                )
        except Loan.DoesNotExist:
            pass

