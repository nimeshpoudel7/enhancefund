import math

from django.db.models import Sum

from borrower.models import Borrower
from enhancefund.Constant import REQUIRED_CREATE_LOAN_FIELD, REQUIRED_CREATE_INVESTMENT_FIELD
from enhancefund.postvalidators import BaseValidator
from enhancefund.rolebasedauth import BaseBorrowerView, BaseInvestorView
from enhancefund.utils import enhance_response
from investor.models import InvestorBalance
from investor.serializers import TransactionSerializer
from loans.models import LoanApplication, Loan, LoanRepaymentSchedule, Investment
from loans.serializers import LoanSerializer, SchedulerSerializer, InvestmentSerializer
from users.models import User
from rest_framework import status
from rest_framework import generics
from django.db import models
from datetime import date, timedelta

class CreateLoan(BaseBorrowerView, BaseValidator, generics.CreateAPIView):
    def calculate_interest_rate(self, payment_frequency):
        base_rate = 10.0  # Base interest rate
        frequency_rates = {
            'monthly': 0,
            '3_monthly': 1.5,
            'one_time': 5.5
        }

        return base_rate + frequency_rates.get(payment_frequency, 0)

    def calculate_total_payable(self, amount, interest_rate, term_months):
        monthly_rate = interest_rate / 100 / 12
        total_payable = amount * (1 + monthly_rate) ** term_months
        return round(total_payable, 2)

    def calculate_number_of_payments(self, term_months, payment_frequency):
        if payment_frequency == 'one_time':
            return 1
        elif payment_frequency == 'monthly':
            return term_months
        elif payment_frequency == '3_monthly':
            return math.ceil(term_months / 3)
        else:
            return term_months  # Default to monthly if frequency is not recognized

    def generate_repayment_schedule(self, loan, total_payable, number_of_payments):
        amount_per_payment = round(total_payable / number_of_payments, 2)
        schedules = []

        for i in range(1, number_of_payments + 1):
            schedule_data = {
                'installment_number': i,
                'due_date': None,
                'amount_due': amount_per_payment,
                'payment_status': 'pending'
            }
            serializer = SchedulerSerializer(data=schedule_data, context={'loan': loan})
            if serializer.is_valid():
                schedules.append(serializer)
            else:
                print(serializer.errors)

        return schedules

    def post(self, request, *args, **kwargs):
        validation_errors = self.validate_data(request.data, REQUIRED_CREATE_LOAN_FIELD)
        if validation_errors:

            return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Please enter required fields")
        user = request.user
        user_id = User.objects.get(email=user.email)
        # calcluate intrest rate logic
        # create frequency

        borrowerDetails = Borrower.objects.filter(user=user_id).first()
        borrower_id = Borrower.objects.get(user=user)

        if borrowerDetails is None:
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="You do not borrower account")
        loanDetails = Loan.objects.filter(borrower=borrowerDetails.id).last()
        if (loanDetails is not None and loanDetails.status != 'repaid' and loanDetails.status != 'defaulted'):
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="You have previous loan which is not closed")

        payment_frequency = request.data.get("payment_frequency")

        interest_rate = self.calculate_interest_rate(payment_frequency)
        amount = float(request.data.get("amount"))
        term_months = int(request.data.get("term_months"))
        total_payable = self.calculate_total_payable(amount, interest_rate, term_months)

        number_of_payments = self.calculate_number_of_payments(term_months, payment_frequency)
        print(number_of_payments)
        data_to_send={
            "amount":amount,
            "loan_purpose":request.data.get("loan_purpose"),
            "term_months": term_months,
            "status":'processing',
            "interest_rate":interest_rate,
            "total_payable":total_payable
        }
        data_to_send = {
            "amount": amount,
            "loan_purpose": request.data.get("loan_purpose"),
            "term_months": term_months,
            "status": 'processing',
            "interest_rate": interest_rate,
            "total_payable": total_payable
        }
        serializer = LoanSerializer(data=data_to_send, context={"borrower": borrower_id})

        if serializer.is_valid():
            loan=serializer.save()
            print(loan.id)
            repayment_schedules = self.generate_repayment_schedule(loan, total_payable, number_of_payments)
            for schedule_serializer in repayment_schedules:
                schedule_serializer.save()


        else:
            print(serializer.errors)
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="Invalid data")

        return enhance_response(data={}, status=status.HTTP_200_OK,
                                    message="Your loan is created successfully")

class ViewLoan(BaseBorrowerView, BaseValidator, generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        user_id = User.objects.get(email=user.email)
        # calcluate intrest rate logic
        # create frequency
        borrower_id = Borrower.objects.get(user=user)
        try:
            loans = Loan.objects.filter(borrower=borrower_id)
            if not loans.exists():
                return enhance_response(
                    data=[],
                    message="No loans found for this borrower",
                    status=status.HTTP_200_OK
                )
            loan_data = []


            print(loan_data)
            for loan in loans:
                serializer = self.get_serializer(loan)
                loan_dict = serializer.data
                funded_amount = Investment.objects.filter(loan=loan).aggregate(Sum('amount'))['amount__sum'] or 0
                remaining_amount = loan.amount - funded_amount

                loan_dict['funded_amount'] = float(funded_amount)
                loan_dict['remaining_amount'] = float(remaining_amount)
                loan_data.append(loan_dict)


            return enhance_response(
                data=loan_data,
                message="Loans retrieved successfully",
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return enhance_response(
                data={},
                message=f"An error occurred: {str(e)}",
                status=status.HTTP_404_NOT_FOUND
            )

class loanList(BaseValidator, generics.ListAPIView):
    # loan fulfil false and also remain amount
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get(self, request, *args, **kwargs):
        try:
            # Retrieve all loans from the Loan model
            loans = Loan.objects.all()

            # If no loans exist, return a 404 response
            if not loans.exists():
                return enhance_response(
                    data={},
                    message="No loans found",
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize the list of loans
            loan_data = []

            print(loan_data)
            for loan in loans:
                serializer = self.get_serializer(loan)
                loan_dict = serializer.data
                funded_amount = Investment.objects.filter(loan=loan).aggregate(Sum('amount'))['amount__sum'] or 0
                remaining_amount = loan.amount - funded_amount

                loan_dict['funded_amount'] = float(funded_amount)
                loan_dict['remaining_amount'] = float(remaining_amount)
                loan_data.append(loan_dict)

            return enhance_response(
                data=loan_data,
                message="Loans retrieved successfully",
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return enhance_response(
                data={},
                message=f"An error occurred: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# create investment
# one loan can have multiple investor
# one investor can give in mulitple loan
# when ammount is fulfill add due date in all investment

class createInvestment(BaseInvestorView, BaseValidator, generics.CreateAPIView):
    serializer_class = InvestmentSerializer

    def update_due_dates(self, loan_id):
        repayment_details = LoanRepaymentSchedule.objects.filter(loan=loan_id)
        num_installments = len(repayment_details)
        start_date = date.today()  # Assuming the loan starts today, adjust as needed

        # Determine EMI frequency based on number of installments
        if num_installments == 1:
            emi_frequency = 'one_time'
        elif num_installments == 4:
            emi_frequency = '3_monthly'
        elif num_installments == 12:
            emi_frequency = 'monthly'
        else:
            raise ValueError(f"Unsupported number of installments: {num_installments}")

        for index, repayment in enumerate(repayment_details):
            if emi_frequency == 'monthly':
                due_date = start_date + timedelta(days=(index + 1) * 30)
            elif emi_frequency == '3_monthly':
                due_date = start_date + timedelta(days=(index + 1) * 90)
            elif emi_frequency == 'one_time':
                due_date = start_date + timedelta(days=30)  # Assuming one-time payment is due in 30 days

            repayment.due_date = due_date
            repayment.save()


    def post(self, request, *args, **kwargs):
        # Validate the required fields
        validation_errors = self.validate_data(request.data, REQUIRED_CREATE_INVESTMENT_FIELD)
        if validation_errors:
            return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Please enter required fields")

        user = request.user
        user_id = User.objects.get(email=user.email)
        loan_id = request.data.get("loan")
        invest_amount = request.data.get("amount")
        borrower_balance=0

        # Check if loan exists
        try:
            loan_details = Loan.objects.get(id=loan_id)

        except Loan.DoesNotExist:
            return enhance_response(
                data={},
                message="Loan not found",
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the loan is already fulfilled
        if loan_details.is_fulfill:
            return enhance_response(
                data={},
                message="Loan is already fulfilled",
                status=status.HTTP_400_BAD_REQUEST
            )
        # Calculate the total amount already invested in the loan
        total_invested = Investment.objects.filter(loan=loan_details).aggregate(total=models.Sum('amount'))['total'] or 0
        remaining_amount = loan_details.amount - total_invested
        borrower_details=Borrower.objects.get(user=loan_details.borrower.user)

        print(remaining_amount,"remaining_amount")
        if invest_amount > remaining_amount:
            return enhance_response(
                data={},
                message=f"Investment amount exceeds the remaining loan amount. Only {remaining_amount} is available.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # If everything is valid, create the investment
        try:
            data = request.data.copy()
            data['loan'] = loan_id
            serializer = InvestmentSerializer(data=data, context={'investor': user, 'loan': loan_details})
            if serializer.is_valid():
                serializer.save()

                new_total_invested = Investment.objects.filter(loan=loan_details).aggregate(total=Sum('amount'))[
                                         'total'] or 0
                remaining_amount = loan_details.amount - new_total_invested
                if remaining_amount==0:
                    to_serialize_data = {
                        "transaction_type": "deposit",
                        "amount": invest_amount,
                        "payment_id": "internal"
                    }
                    loan_details.is_fulfill=True
                    loan_details.status='approved'
                    loan_details.save()
                    self.update_due_dates(loan_id)
                    borrower_details.account_balance=float(borrower_details.account_balance+loan_details.amount)
                    borrower_details.save()
                    serializerTransactionBorrower = TransactionSerializer(data=to_serialize_data, context={"user": user_id})
                    serializerTransactionBorrower.is_valid()
                    serializerTransactionBorrower.save()
                investor_balance = InvestorBalance.objects.get(user=user_id)
                investor_balance.account_balance=investor_balance.account_balance-invest_amount
                investor_balance.save()
                to_serialize_data = {
                    "transaction_type": "investment",
                    "amount": invest_amount,
                    "payment_id": "internal"
                }
                serializerTransaction = TransactionSerializer(data=to_serialize_data, context={"user": user_id})
                serializerTransaction.is_valid()
                serializerTransaction.save()
                # and also create transaction



                return enhance_response(
                    data=serializer.data,
                    message="Investment created successfully",
                    status=status.HTTP_201_CREATED
                )
            else:
                print(serializer.errors)
                return enhance_response(
                    data={},
                    message="Investment created fail",
                    status=status.HTTP_400_BAD_REQUEST
                )


        except Exception as e:
            return enhance_response(
                data={},
                message=f"An error occurred: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
