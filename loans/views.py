import math

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils import timezone

from borrower.models import Borrower, CreditScoreHistory
from borrower.serializer import CreditScoreHistorySerializer, BorrowerSerializer
from enhancefund.Constant import REQUIRED_CREATE_LOAN_FIELD, REQUIRED_CREATE_INVESTMENT_FIELD, \
    REQUIRED_LOAN_REPAYMENT_FIELD
from enhancefund.postvalidators import BaseValidator
from enhancefund.rolebasedauth import BaseBorrowerView, BaseInvestorView
from enhancefund.utils import enhance_response, create_payment_link_for_customer, check_Add_fund_status
from investor.models import InvestorBalance
from investor.serializers import TransactionSerializer, PaymentHistorySerializer
from loans.models import LoanApplication, Loan, LoanRepaymentSchedule, Investment, PaymentHistory, Transaction
from loans.serializers import LoanSerializer, SchedulerSerializer, InvestmentSerializer, EmiSerializer
from users.models import User
from rest_framework import status
from rest_framework import generics
from django.db import models
from datetime import date, timedelta, datetime
from decimal import Decimal

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
        data_to_send = {
            "amount": amount,
            "loan_amount":amount*0.97,
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
            print(loans)
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
                borrower = loan.borrower
                borrower_data = BorrowerSerializer(borrower).data  # Use the correct serializer for the borrower
                credit_score_history = CreditScoreHistory.objects.filter(borrower=borrower)
                credit_score_history_data = CreditScoreHistorySerializer(credit_score_history, many=True).data

                serializer = self.get_serializer(loan)
                loan_dict = serializer.data
                funded_amount = Investment.objects.filter(loan=loan).aggregate(Sum('amount'))['amount__sum'] or 0
                remaining_amount = loan.amount - funded_amount
                loan_dict['credit_score_history'] = credit_score_history_data
                loan_dict['borrower'] = borrower_data

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
            start_date = date.today()
            closed_date = start_date + relativedelta(months=loan_details.term_months)
            # Add this line to convert date to datetime:
            closed_datetime = datetime.combine(closed_date, datetime.min.time())

            data = request.data.copy()
            data['loan'] = loan_id
            data['closed_at'] = closed_datetime

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
                    borrower_details.account_balance=float(borrower_details.account_balance+loan_details.loan_amount)
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


class expectedReturn(BaseInvestorView, BaseValidator, generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get(self, request, *args, **kwargs):
        loan_id = float(request.query_params.get('loan_id'))
        amount = Decimal(request.query_params.get('amount'))  # Convert to Decimal
        year = Decimal(request.query_params.get('year'))  # Convert to Decimal

        user = request.user
        user_id = User.objects.get(email=user.email)

        # Check if loan exists
        try:
            loan_details = Loan.objects.get(id=loan_id)
            interest_rate = Decimal(loan_details.interest_rate) * Decimal(0.97)

            # Perform the calculation using Decimal for precision
            future_value = amount * (1 + (interest_rate * year / Decimal(100)))
            print(interest_rate, "aaa")
            data_to_send={
                'amount':amount,
                'net_return':future_value,
                'interest_rate':interest_rate
            }
            return enhance_response(
                data=data_to_send,
                message="Data fetch successfully",
                status=status.HTTP_200_OK
            )



        except Loan.DoesNotExist:
            return enhance_response(
                data={},
                message="Loan not found",
                status=status.HTTP_404_NOT_FOUND
            )

class myInvestment(BaseInvestorView, BaseValidator, generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get(self, request, *args, **kwargs):

        user = request.user

        # Check if loan exists
        try:
            loans = Investment.objects.filter(investor=user.id)
            data_to_send = []
            # data_to_send={
            #     'data':loans,
            # }
            for investment in loans:
                loan_data = {
                    'loan_id': investment.loan.id,
                    'loan_amount': investment.loan.amount,
                    'loan_purpose':investment.loan.loan_purpose,
                    'term_months': investment.loan.term_months,
                    'is_fulfill':investment.loan.is_fulfill
                    # 'loan_interest_rate':,
                }
                print(investment)
                interest_rate = Decimal(investment.loan.interest_rate) * Decimal(0.97)
                borrower_details = {
                    'first_Name':investment.loan.borrower.user.first_name,
                    'Last_Namee':investment.loan.borrower.user.last_name
                 }
                print()
                data_to_send.append({
                    'id': investment.id,
                    'investor_id': investment.investor.id,
                    'amount': investment.amount,
                    'net_return': investment.net_return,
                    'created_at': investment.created_at,
                    'interest_rate':interest_rate,
                    'status': investment.status,
                    'close_date': investment.closed_at,
                    'loan': loan_data,
                    'borrower_details':borrower_details
                })

            return enhance_response(
                data=data_to_send,
                message="Data fetch successfully",
                status=status.HTTP_200_OK
            )



        except Loan.DoesNotExist:
            return enhance_response(
                data={},
                message="Loan not found",
                status=status.HTTP_404_NOT_FOUND
            )


class PortfolioValue(BaseInvestorView, BaseValidator, generics.RetrieveAPIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            # Get all investments for the user
            investments = Investment.objects.filter(investor=user.id)

            # Initialize portfolio metrics
            portfolio_metrics = {
                'total_invested': Decimal('0.00'),
                'total_expected_return': Decimal('0.00'),
                'total_actual_return': Decimal('0.00'),
                'portfolio_value': Decimal('0.00'),
                'total_loans': 0,
                'investments_by_loan_purpose': {},
                'investment_history': []
            }

            # Get unique loan purposes
            unique_loans = set()

            # Calculate portfolio metrics
            for investment in investments:
                # Add to total invested
                portfolio_metrics['total_invested'] += investment.amount

                # Calculate returns
                interest_rate = Decimal(investment.loan.interest_rate) * Decimal('0.97')
                if investment.net_return:
                    portfolio_metrics['total_actual_return'] += investment.net_return
                else:
                    expected_return = investment.amount * (interest_rate / Decimal('100'))
                    portfolio_metrics['total_expected_return'] += expected_return

                # Track unique loans
                unique_loans.add(investment.loan.id)

                # Group by loan purpose
                loan_purpose = investment.loan.loan_purpose
                if loan_purpose not in portfolio_metrics['investments_by_loan_purpose']:
                    portfolio_metrics['investments_by_loan_purpose'][loan_purpose] = {
                        'total_amount': Decimal('0.00'),
                        'count': 0
                    }
                portfolio_metrics['investments_by_loan_purpose'][loan_purpose]['total_amount'] += investment.amount
                portfolio_metrics['investments_by_loan_purpose'][loan_purpose]['count'] += 1

                # Add to investment history
                portfolio_metrics['investment_history'].append({
                    'date': investment.created_at,
                    'amount': investment.amount,
                    'loan_purpose': loan_purpose,
                    'interest_rate': interest_rate,
                    'net_return': investment.net_return
                })

            # Calculate final portfolio value
            portfolio_metrics['portfolio_value'] = (
                    portfolio_metrics['total_invested'] +
                    portfolio_metrics['total_actual_return'] +
                    portfolio_metrics['total_expected_return']
            )

            # Calculate total number of loans
            portfolio_metrics['total_loans'] = len(unique_loans)

            # Format decimal values to 2 decimal places
            for key in ['total_invested', 'total_expected_return', 'total_actual_return', 'portfolio_value']:
                portfolio_metrics[key] = float(portfolio_metrics[key].quantize(Decimal('0.01')))

            # Format loan purpose metrics
            for purpose in portfolio_metrics['investments_by_loan_purpose']:
                portfolio_metrics['investments_by_loan_purpose'][purpose]['total_amount'] = float(
                    portfolio_metrics['investments_by_loan_purpose'][purpose]['total_amount'].quantize(Decimal('0.01'))
                )

            return enhance_response(
                data=portfolio_metrics,
                message="Portfolio value calculated successfully",
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return enhance_response(
                data={},
                message=f"Error calculating portfolio value: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class checkRepaymentBorrower(BaseBorrowerView, BaseValidator, generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        user_id = User.objects.get(email=user.email)
        loan_id = request.data.get("loan_id")
        if not loan_id:
            return enhance_response(
                data={},
                message="No Loan Details found.",
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if loan exists
        try:
            borrowerDetails = Borrower.objects.filter(user=user_id).first()
            if not borrowerDetails:
                return enhance_response(
                    data={},
                    message="No borrower details found.",
                    status=status.HTTP_404_NOT_FOUND
                )

            borrower_id = Borrower.objects.get(user=user)
            loanDetails = Loan.objects.filter(borrower=borrower_id.id,id=loan_id)

            response_data = []

            for loan in loanDetails:
                if loan.status != 'repaid':
                    repayment_details = LoanRepaymentSchedule.objects.filter(loan=loan.id)
                    print(repayment_details)
                    for repayment in repayment_details:
                        installment_data = {
                            'loan_id': loan.id,  # Add the loan ID here
                            'installment_number': repayment.installment_number,
                            'repayment_id': repayment.id,
                            'due_date': repayment.due_date,
                            'payment_status': repayment.payment_status,
                            'amount_paid': repayment.amount_paid,
                            'amount_due': repayment.amount_due,
                        }

                        # Check due date logic
                        now = timezone.now()
                        due_date = repayment.due_date

                        if repayment.payment_status == 'pending' or repayment.payment_status == 'missed':  # Use repayment.payment_status instead
                            if due_date > now:  # Not yet due
                                days_left = (due_date - now).days
                                if days_left <= 15:
                                    installment_data['notification'] = 'Due in less than 15 days'
                            else:  # Due date has passed
                                installment_data['payment_status'] = 'missed'

                                # Check if the increase can be applied
                                if not repayment.last_missed_date or (
                                        repayment.last_missed_date.month != now.month and repayment.last_missed_date.year == now.year):
                                    missed_amount = float(repayment.amount_due) * 1.05  # Increase by 5%
                                    repayment.amount_due = f"{missed_amount:.2f}"  # Format to two decimal places
                                    repayment.last_missed_date = now  # Update last missed date
                                    repayment.payment_status='missed'
                                    repayment.save()  # Save the updated repayment
                                installment_data['amount_due'] = repayment.amount_due

                        # Check if payment is enabled for missed installment
                        if repayment.payment_status == 'missed' or (due_date - now).days <= 15:
                            installment_data['is_payment_enabled'] = True
                        else:
                            installment_data['is_payment_enabled'] = False

                        response_data.append(installment_data)

            return enhance_response(
                data=response_data,
                message="Repayment details retrieved successfully.",
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return enhance_response(
                data={},
                message=f"Error retrieving repayment details: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class loanRepayment(BaseBorrowerView, BaseValidator, generics.GenericAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def post(self, request, *args, **kwargs):


        # Check if loan exists
        try:
            # Validate the required fields
            validation_errors = self.validate_data(request.data, REQUIRED_LOAN_REPAYMENT_FIELD)
            if validation_errors:
                return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                        message="Please enter required fields")

            user = request.user
            user_id = User.objects.get(email=user.email)
            loan_id = request.data.get("loan_id")
            repayment_id = request.data.get("repayment_id")
            repayment_details = LoanRepaymentSchedule.objects.filter(id=repayment_id)
            if len(repayment_details)==0:
                return enhance_response(
                    data={},
                    message="No such repayment id",
                    status=status.HTTP_400_BAD_REQUEST
                )

            for repayment in repayment_details:
                if repayment.loan.id !=loan_id:
                    return enhance_response(
                        data={},
                        message="Loan id is not matched",
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if repayment.payment_status=='paid':
                    return enhance_response(
                        data={},
                        message="Your EMI is already paid",
                        status=status.HTTP_400_BAD_REQUEST
                    )
            #     create stripe payment link
                stripe_customer_id = user_id.stripe_customer_id
                amount=repayment.amount_due
                payment_link = create_payment_link_for_customer(stripe_customer_id,amount,repayment_id)
                # #  add to table
                if not payment_link:
                    return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                            message="Unable to pay,  please try again")
                to_serialize_data = {
                    "payment_amount": amount,
                    "stripe_payment_id": payment_link.id
                }
                serializer = PaymentHistorySerializer(data=to_serialize_data, context={"user": user_id})
                if serializer.is_valid():
                    serializer.save()
                    response_data = dict(serializer.data)
                    response_data["url"] = payment_link.url
                    return enhance_response(data=response_data, message="Payment Link generated Successfully",
                                            status=200)
                else:
                    return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                                            message="Invalid data")

        except Exception as e:
            return enhance_response(
                data={},
                message=f"Error retrieving repayment details: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST
            )


class checkRefundStatus(BaseBorrowerView,BaseValidator,generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        payment_id = request.query_params.get('payment_id')
        repayment_id = request.query_params.get('repayment_id')


        user = request.user
        user_id = User.objects.get(email=user.email)
        stripe_history = {}
        if not repayment_id and not payment_id:
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="Invalid Data")

        stripe_history=check_Add_fund_status(payment_id)

        if  stripe_history.status != "complete":
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="payment is incomplete")

        to_serialize_data = {
            "transaction_type": "payment",
            "amount": stripe_history.amount_total/100,
            "payment_id": payment_id
        }

        try:
            transaction_entry = Transaction.objects.get(payment_id=payment_id)
            if(transaction_entry):
                return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                        message="You have already paid for this payment id")
        except:

            serializer = TransactionSerializer(data=to_serialize_data, context={"user": user_id})
            if not serializer.is_valid():
                return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                        message="unable to pay fund")
            serializer.save()
            try:
                #   update repayment table
                borrower_id = Borrower.objects.get(user=user)
                loanDetails = Loan.objects.filter(borrower=borrower_id.id).last()
                repayment_details = LoanRepaymentSchedule.objects.filter(loan=loanDetails.id)
                amountPaid=stripe_history.amount_total/100
                for repayment in repayment_details:
                    amountToBePaid=repayment.amount_due
                    if(int(repayment_id)==int(repayment.id)):
                        finalRepayment = LoanRepaymentSchedule.objects.get(id=repayment.id)
                        finalRepayment.payment_status='paid'
                        finalRepayment.amount_paid=float(amountPaid)
                        finalRepayment.amount_due=float(amountToBePaid)-float(amountPaid)
                        finalRepayment.save()
                        to_serialize_data_emi = {
                            "transaction_type": "payment",
                            "amount": float(amountPaid),
                            "stripe_payment_id": payment_id,
                            'status':"completed"
                        }

                        serializerEmi = EmiSerializer(data=to_serialize_data_emi, context={"loan": loanDetails})
                        serializerEmi.is_valid()
                        serializerEmi.save()

                CheckAllRepayment = LoanRepaymentSchedule.objects.filter(loan=loanDetails)
                all_paid = True

                for eachRepayment in CheckAllRepayment:
                    print(eachRepayment.payment_status)
                    if eachRepayment.payment_status.lower() != 'paid':
                        all_paid = False
                        break
                if all_paid:
                    print("update loan")
                    loanDetails.status='repaid'
                    loanDetails.save()
                return enhance_response(data=[], message="Payment is completed",
                                                status=200)

            except Exception as e:

                return enhance_response(

                    data={},

                    message=f"Error while repayment : {str(e)}",

                    status=status.HTTP_400_BAD_REQUEST

                )