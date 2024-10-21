from datetime import timezone

from django.shortcuts import render
from rest_framework.exceptions import ValidationError

from borrower.models import Borrower
from enhancefund.Constant import REQUIRED_ADD_FUND_FIELDS
from enhancefund.postvalidators import BaseValidator
from enhancefund.rolebasedauth import BaseInvestorView, BaseAuthenticatedView
from rest_framework import generics

from enhancefund.utils import enhance_response, create_payment_link_for_customer, check_Add_fund_status, transfer_funds, \
    create_payout
from investor.models import InvestorBalance
from investor.serializers import PaymentHistorySerializer, TransactionSerializer, InvestorBalanceSerializer
from loans.models import PaymentHistory, Transaction, Investment, LoanRepaymentSchedule
from loans.serializers import InvestmentSerializer
from users.models import User
from rest_framework import status
from decimal import Decimal


# Create your views here.

class InvestorAddFunds(BaseInvestorView,BaseValidator,generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        validation_errors = self.validate_data(request.data, REQUIRED_ADD_FUND_FIELDS)
        if validation_errors:
            return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Please enter required fields")

        user = request.user
        user_id = User.objects.get(email=user.email)  # Corrected line
        stripe_customer_id=user_id.stripe_customer_id
        amount=request.data.get('amount')
        payment_link=create_payment_link_for_customer(stripe_customer_id,amount,"xvKjmlKNp11")
        #  add to table
        if not payment_link:
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="Unable to add fund please try again")
        to_serialize_data={
            "payment_amount" :request.data.get('amount'),
            "stripe_payment_id": payment_link.id

        }
        serializer=PaymentHistorySerializer(data=to_serialize_data, context={"user": user_id})
        if serializer.is_valid():
            serializer.save()
            response_data = dict(serializer.data)
            response_data["url"] = payment_link.url
            return enhance_response(data=response_data, message="Payment Link generated Successfully", status=200)
        else:
            return enhance_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Invalid data")


class CheckFundStatus(BaseInvestorView,BaseValidator,generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        payment_id = request.query_params.get('payment_id')
        user = request.user
        user_id = User.objects.get(email=user.email)
        stripe_history = {}
        if not payment_id:
            # check_Add_fund_status

            paymentHistory = PaymentHistory.objects.filter(user=user).order_by(
                '-payment_date').first()
            payment_id=paymentHistory.stripe_payment_id
            stripe_history=check_Add_fund_status(paymentHistory.stripe_payment_id)
        else:
            stripe_history=check_Add_fund_status(payment_id)

        if  stripe_history.status != "complete":
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="Invalid data")

#       # add  in transaction table add
#  add in investorbalance table

#         check whether that payment id value is inserted
#  to avoid double add for same add fund
#         serializer=PaymentHistorySerializer(data=to_serialize_data, context={"user": user_id})
        to_serialize_data = {
            "transaction_type": "deposit",
            "amount": stripe_history.amount_total/100,
            "payment_id": payment_id
        }

        try:
            transaction_entry = Transaction.objects.get(payment_id=payment_id)
            print(transaction_entry, "transaction_entry", payment_id)
            if(transaction_entry):
                return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                        message="Fund is already added to your wallet")
        except:

            serializer = TransactionSerializer(data=to_serialize_data, context={"user": user_id})
            if not serializer.is_valid():
                return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                        message="unable to add fund")
            serializer.save()
            investor_balance = InvestorBalance.objects.filter(user=user_id).first()
            balance = {
            }
            if investor_balance is None:
                balance["account_balance"]=stripe_history.amount_total / 100
                serializerInvestor = InvestorBalanceSerializer(data=balance, context={"user": user_id})
                if serializerInvestor.is_valid():
                     serializerInvestor.save()
                     return enhance_response(data=serializerInvestor.data, status=status.HTTP_200_OK,
                                        message="Your fund is added Successfully")
            else:
               new_added_amount=stripe_history.amount_total / 100
               balance["account_balance"] =Decimal(investor_balance.account_balance)+ Decimal(new_added_amount)
               serializerInvestor = InvestorBalanceSerializer(investor_balance,data=balance, partial=True,
                                                   context={"user": user_id})
               if serializerInvestor.is_valid():
                   serializerInvestor.save()
                   return enhance_response(data=serializerInvestor.data, status=status.HTTP_200_OK,
                                    message="Your fund is added Successfully")


class WalletBalance(BaseInvestorView,BaseValidator,generics.RetrieveAPIView):
    queryset = InvestorBalance.objects.all()
    serializer_class = InvestorBalanceSerializer

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            investor_balance = InvestorBalance.objects.get(user=user)
            serializer = self.get_serializer(investor_balance)
            return enhance_response(
                data=serializer.data,
                message="Wallet balance retrieved successfully",
                status=status.HTTP_200_OK
            )
        except InvestorBalance.DoesNotExist:
            return enhance_response(
                data={},
                message="No wallet balance found for this user",
                status=status.HTTP_404_NOT_FOUND
            )

class WithdrawBalance(BaseAuthenticatedView,BaseValidator,generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            validation_errors = self.validate_data(request.data, REQUIRED_ADD_FUND_FIELDS)
            if validation_errors:
                return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                        message="Please enter required fields")
            user_balance=0
            print(user.role)
            if user.role=="borrower":
                user_balance = Borrower.objects.filter(user=user.id).first()
            else:
                user_balance = InvestorBalance.objects.filter(user=user.id).first()


            requested_amount=request.data.get("amount")
            print(user_balance)
            if user_balance.account_balance<requested_amount:
                return enhance_response(
                    data={},
                    message="In sufficient balance",
                    status=status.HTTP_400_BAD_REQUEST
                )
            stripe_response=create_payout(requested_amount,user.stripe_account_id)
            stripe_response_transfer=transfer_funds(requested_amount,user.stripe_account_id)
            if user.role == "borrower":
                borrower_details = Borrower.objects.filter(user=user.id).first()
                borrower_details.account_balance=float(borrower_details.account_balance-requested_amount)
                borrower_details.save()
            else:
                investor_details = InvestorBalance.objects.filter(user=user.id).first()
                investor_details.account_balance = float(investor_details.account_balance - requested_amount)
                investor_details.save()
                user_id = User.objects.get(email=user.email)

            to_serialize_data = {
                "transaction_type": "withdrawal",
                "amount": requested_amount,
                "payment_id": "internal"
            }
            serializerTransactionBorrower = TransactionSerializer(data=to_serialize_data, context={"user": user_id})
            serializerTransactionBorrower.is_valid()
            serializerTransactionBorrower.save()
            return enhance_response(
                    message="Withdraw is completed",
                    status=status.HTTP_200_OK
                )
            print(stripe_response)
        except:
            return enhance_response(
                data={},
                message="Something went wrong",
                status=status.HTTP_400_BAD_REQUEST
            )


class InvestmentClosureProcess(BaseInvestorView, BaseValidator, generics.GenericAPIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def get(self, request, *args, **kwargs):
        from django.utils import timezone
        user = request.user
        current_date = timezone.now()

        try:
            pending_closures = Investment.objects.filter(
                investor=user,
                status='Open',
                closed_at__lte=current_date
            ).select_related('loan')

            if not pending_closures.exists():
                return enhance_response(
                    data={},
                    message="No pending closures found for your investments",
                    status=status.HTTP_200_OK
                )
            current_date = timezone.now()
            response_data = []
            balance={}
            sum=0
            user_id = User.objects.get(email=user.email)

            for investment in pending_closures:
                loan = investment.loan
                has_repayments = LoanRepaymentSchedule.objects.filter(
                    loan=loan,
                    payment_status='paid'
                ).exists()
                print(has_repayments)
                if has_repayments and investment.net_return > 0:
                    try:
                        transaction_data = {
                            "transaction_type": "investment_return",
                            "amount": float(investment.net_return),
                            "status": "completed",
                            "description": f"Net return for investment {investment.id}"
                        }

                        transaction_serializer = TransactionSerializer(
                            data=transaction_data,
                            context={"user": user}
                        )

                        if transaction_serializer.is_valid():
                            transaction = transaction_serializer.save()
                            sum=sum+investment.net_return

                            # Update investment status
                            investment.status = 'closed'
                            investment.closed_at = current_date
                            investment.save()

                            response_data.append({
                                'investment_id': investment.id,
                                'loan_id': loan.id,
                                'amount_invested': float(investment.amount),
                                'net_return': float(investment.net_return),
                                'transaction_id': transaction.id,
                                'original_closure_date': investment.closed_at,
                                'actual_closure_date': current_date.date(),
                                'status': 'closed'
                            })
                        else:
                            raise ValidationError(transaction_serializer.errors)

                    except Exception as e:
                        response_data.append({
                            'investment_id': investment.id,
                            'loan_id': loan.id,
                            'error': str(e),
                            'status': 'failed',
                            'original_closure_date': investment.closed_at
                        })
                        continue
            investor_balance = InvestorBalance.objects.filter(user=user_id).first()
            new_added_amount =sum
            balance["account_balance"] = Decimal(investor_balance.account_balance) + Decimal(new_added_amount)
            serializerInvestor = InvestorBalanceSerializer(investor_balance, data=balance, partial=True,
                                                           context={"user": user_id})
            serializerInvestor.is_valid()
            serializerInvestor.save()
            if response_data:
                return enhance_response(
                    data=response_data,
                    message="Investment closures processed successfully",
                    status=status.HTTP_200_OK
                )
            else:
                return enhance_response(
                    data={},
                    message="No eligible investments found for closure",
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return enhance_response(
                data={},
                message=f"Error processing investment closures: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )