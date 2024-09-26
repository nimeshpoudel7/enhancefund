# loans/cron.py
from .models import LoanRequest
from .utils import send_payment_reminder
from datetime import date


def send_daily_payment_reminders():
    loans = LoanRequest.objects.filter(next_payment_date=date.today())
    for loan in loans:
        send_payment_reminder(loan)
