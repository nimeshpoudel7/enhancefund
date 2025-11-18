# utils/email_utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Optional, Dict
from datetime import datetime, timedelta


class EmailService:
    @staticmethod
    def send_email(
            subject: str,
            to_email: List[str],
            template_name: str,
            context: Dict = None,
            from_email: str = None
    ) -> bool:
        try:
            sender = from_email or settings.DEFAULT_FROM_EMAIL

            html_message = render_to_string(
                f'emails/{template_name}.html',
                context or {}
            )

            text_message = render_to_string(
                f'emails/{template_name}.txt',
                context or {}
            )

            send_mail(
                subject=subject,
                message=text_message,
                from_email=sender,
                recipient_list=to_email,
                html_message=html_message,
                fail_silently=False
            )
            return True

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_welcome_email(user) -> bool:
        context = {
            'first_name': user.first_name,
            'username': user.username,
            'site_name': 'Your Site Name'
        }
        return EmailService.send_email(
            subject='Welcome to Our Platform',
            to_email=[user.email],
            template_name='welcome_email',
            context=context
        )

    @staticmethod
    def send_funds_added_notification(user, amount: float, transaction_id: str) -> bool:
        """Send notification when funds are successfully added to account"""
        context = {
            'first_name': user.first_name,
            'amount': amount,
            'transaction_id': transaction_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_balance': user.balance if hasattr(user, 'balance') else None
        }

        return EmailService.send_email(
            subject='Funds Added Successfully',
            to_email=[user.email],
            template_name='funds_added',
            context=context
        )

    @staticmethod
    def send_loan_approval_notification(
            user,
            loan_amount: float,
            interest_rate: float,
            tenure: int,
            emi_amount: float,
            first_emi_date: datetime
    ) -> bool:
        """Send notification when loan is approved"""
        context = {
            'first_name': user.first_name,
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'tenure': tenure,
            'emi_amount': emi_amount,
            'first_emi_date': first_emi_date.strftime('%Y-%m-%d'),
            'last_emi_date': (first_emi_date + timedelta(days=30 * tenure)).strftime('%Y-%m-%d')
        }

        return EmailService.send_email(
            subject='Loan Approved! 🎉',
            to_email=[user.email],
            template_name='loan_approved',
            context=context
        )

    @staticmethod
    def send_repayment_success_notification(
            user,
            payment_amount: float,
            loan_id: str,
            remaining_balance: float
    ) -> bool:
        """Send notification when repayment is successfully processed"""
        context = {
            'first_name': user.first_name,
            'payment_amount': payment_amount,
            'loan_id': loan_id,
            'payment_date': datetime.now().strftime('%Y-%m-%d'),
            'remaining_balance': remaining_balance,
            'is_loan_closed': remaining_balance <= 0
        }

        return EmailService.send_email(
            subject='Loan Repayment Successful',
            to_email=[user.email],
            template_name='repayment_success',
            context=context
        )

    @staticmethod
    def send_upcoming_repayment_reminder(
            user,
            due_date: datetime,
            emi_amount: float,
            loan_id: str,
            days_left: int
    ) -> bool:
        """Send reminder for upcoming repayment"""
        context = {
            'first_name': user.first_name,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'emi_amount': emi_amount,
            'loan_id': loan_id,
            'days_left': days_left,
            'payment_link': f"{settings.SITE_URL}/make-payment/{loan_id}"
        }

        return EmailService.send_email(
            subject=f'Repayment Due in {days_left} Days',
            to_email=[user.email],
            template_name='repayment_reminder',
            context=context
        )

    @staticmethod
    def send_registration_confirmation(user, verification_link: str) -> bool:
        """Send registration confirmation email with verification link"""
        context = {
            'first_name': user.first_name,
            'username': user.username,
            'verification_link': verification_link,
            'site_name': settings.SITE_NAME,
            'valid_hours': 24,  # Link validity period
            'support_email': settings.SUPPORT_EMAIL
        }

        return EmailService.send_email(
            subject='Welcome! Please Verify Your Email',
            to_email=[user.email],
            template_name='registration_confirmation',
            context=context
        )

    @staticmethod
    def send_password_reset_email(user, reset_token: str) -> bool:
        """Send password reset link"""
        reset_link = f"{settings.SITE_URL}/reset-password/{reset_token}"
        context = {
            'first_name': user.first_name,
            'reset_link': reset_link,
            'valid_hours': 24,
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL
        }
        return EmailService.send_email(
            subject='Password Reset Request',
            to_email=[user.email],
            template_name='password_reset',
            context=context
        )

    @staticmethod
    def send_password_changed_notification(user) -> bool:
        """Send notification when password is changed"""
        context = {
            'first_name': user.first_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL
        }

        return EmailService.send_email(
            subject='Your Password Has Been Changed',
            to_email=[user.email],
            template_name='password_changed',
            context=context
        )

    @staticmethod
    def send_email_verification_reminder(user, verification_link: str) -> bool:
        """Send reminder to verify email address"""
        context = {
            'first_name': user.first_name,
            'verification_link': verification_link,
            'valid_hours': 24,
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL
        }

        return EmailService.send_email(
            subject='Please Verify Your Email Address',
            to_email=[user.email],
            template_name='email_verification_reminder',
            context=context
        )

    @staticmethod
    def send_suspicious_login_alert(
            user,
            login_time: datetime,
            device_info: str,
            ip_address: str,
            location: str
    ) -> bool:
        """Send alert for suspicious login activity"""
        context = {
            'first_name': user.first_name,
            'login_time': login_time.strftime('%Y-%m-%d %H:%M:%S'),
            'device_info': device_info,
            'ip_address': ip_address,
            'location': location,
            'support_email': settings.SUPPORT_EMAIL,
            'site_name': settings.SITE_NAME
        }

        return EmailService.send_email(
            subject='Security Alert: New Login Detected',
            to_email=[user.email],
            template_name='suspicious_login',
            context=context
        )