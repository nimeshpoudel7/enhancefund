from django.conf import settings
from django.core.mail import send_mail


def calculate_risk_rating(borrower_profile):
    credit_score = borrower_profile.credit_score
    if credit_score >= 750:
        return 'Low'
    elif credit_score >= 650:
        return 'Medium'
    else:
        return 'High'


# loans/utils.py


def send_payment_reminder(loan):
    subject = 'Payment Reminder'
    message = f'Dear {loan.borrower.user.first_name}, your payment is due on {
        loan.next_payment_date}.'
    recipient_list = [loan.borrower.user.email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
