from datetime import timezone, timedelta
from dbm import error
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone as django_timezone

from django.forms import model_to_dict
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
from loans.models import PaymentHistory, Transaction, Investment, LoanRepaymentSchedule, Loan
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


class WalletBalance(BaseAuthenticatedView,BaseValidator,generics.RetrieveAPIView):


    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            if user.role == "borrower":
                borrower_balance = Borrower.objects.get(user=user)
                balance_data = model_to_dict(borrower_balance)  # Convert InvestorBalance instance to a dict

            else:
                investor_balance = InvestorBalance.objects.get(user=user)
                balance_data = model_to_dict(investor_balance)  # Convert InvestorBalance instance to a dict

            print(user.role)

            return enhance_response(
                data=balance_data,
                message="Wallet balance retrieved successfully",
                status=status.HTTP_200_OK
            )
        except :
            return enhance_response(
                data={},
                message="No wallet balance found for this user",
                status=status.HTTP_404_NOT_FOUND
            )

class WithdrawBalance(BaseAuthenticatedView,BaseValidator,generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        user_id = User.objects.get(email=user.email)

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


            requested_amount = Decimal(str(request.data.get("amount")))
            print(user_balance.account_balance,"aaaaa")
            print(requested_amount,"aaa111aa")
            print(f"Balance type: {type(user_balance.account_balance)}, Requested type: {type(requested_amount)}")
            if user_balance.account_balance < requested_amount:
                return enhance_response(
                    data={},
                    message="In sufficient balance",
                    status=status.HTTP_400_BAD_REQUEST
                )
            stripe_response=create_payout(requested_amount,user.stripe_account_id)
            stripe_response_transfer=transfer_funds(requested_amount,user.stripe_account_id)
            print(stripe_response)
            print(stripe_response_transfer)
            if user.role == "borrower":
                borrower_details = Borrower.objects.filter(user=user.id).first()
                borrower_details.account_balance=float(borrower_details.account_balance-requested_amount)
                borrower_details.save()
            else:
                investor_details = InvestorBalance.objects.filter(user=user.id).first()
                investor_details.account_balance = float(investor_details.account_balance - requested_amount)
                investor_details.save()
                user_id = User.objects.get(email=user.email)
            print("11111111")

            to_serialize_data = {
                "transaction_type": "withdrawal",
                "amount": requested_amount,
                "payment_id": "internal"
            }

            serializerTransactionBorrower = TransactionSerializer(data=to_serialize_data, context={"user": user_id})
            is_valid=serializerTransactionBorrower.is_valid()

            if not is_valid:
                print("Validation failed. Errors:", serializerTransactionBorrower.errors)
            else:
                print("Validation successful. Saving data...")
                serializerTransactionBorrower.save()

            print("aaaaa")
            return enhance_response(
                message="Your request is in processing",
                status=status.HTTP_200_OK
                )
        except Exception as e:
            print("Unhandled exception:", str(e))
            return enhance_response(
                data={},
                message="An unexpected error occurred.",
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
                print(has_repayments,"has_repayments")
                if has_repayments and investment.net_return > 0:
                    try:
                        transaction_data = {
                            "transaction_type": "deposit",
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
            new_added_amount = sum
            print(new_added_amount, sum,"aaaaaa")
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


class RecentTancation(BaseInvestorView, BaseValidator, generics.GenericAPIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        user_id = User.objects.get(email=user.email)
        TransactionData = Transaction.objects.filter(user=user).order_by('-id')[:3]
        serialized_data = TransactionSerializer(TransactionData, many=True).data
        print(serialized_data)
        return enhance_response(
            data=serialized_data,
            message="Investment closures processed successfully",
            status=status.HTTP_200_OK
        )


class InvestmentPerformanceChart(BaseInvestorView, BaseValidator, generics.GenericAPIView):
    """
    API endpoint for Investment Performance Chart Data
    Returns data for line charts, bar charts, and area charts showing:
    - Investment performance over time (monthly)
    - Returns over time
    - Cumulative investment value
    - Transaction trends
    """
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            # Get query parameters for filtering
            period = request.query_params.get('period', '12')  # Default 12 months
            period_type = request.query_params.get('period_type', 'month')  # month, quarter, year
            
            try:
                period = int(period)
            except ValueError:
                period = 12
            
            # Calculate date range
            end_date = django_timezone.now()
            if period_type == 'month':
                start_date = end_date - timedelta(days=period * 30)
            elif period_type == 'quarter':
                start_date = end_date - timedelta(days=period * 90)
            elif period_type == 'year':
                start_date = end_date - timedelta(days=period * 365)
            else:
                start_date = end_date - timedelta(days=period * 30)
            
            # Get all investments for the user
            investments = Investment.objects.filter(
                investor=user,
                created_at__gte=start_date
            ).select_related('loan').order_by('created_at')
            
            # Get all transactions for the user
            transactions = Transaction.objects.filter(
                user=user,
                transaction_date__gte=start_date
            ).order_by('transaction_date')
            
            # Monthly investment aggregation
            monthly_investments = investments.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                total_amount=Sum('amount'),
                count=Count('id')
            ).order_by('month')
            
            # Monthly returns aggregation
            monthly_returns = investments.filter(
                net_return__isnull=False,
                net_return__gt=0
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                total_returns=Sum('net_return')
            ).order_by('month')
            
            # Monthly transaction aggregation
            monthly_transactions = transactions.annotate(
                month=TruncMonth('transaction_date')
            ).values('month', 'transaction_type').annotate(
                total_amount=Sum('amount'),
                count=Count('id')
            ).order_by('month')
            
            # Prepare chart data
            chart_data = {
                'line_chart': {
                    'labels': [],
                    'datasets': [
                        {
                            'label': 'Total Invested',
                            'data': [],
                            'borderColor': 'rgb(75, 192, 192)',
                            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                            'tension': 0.1
                        },
                        {
                            'label': 'Total Returns',
                            'data': [],
                            'borderColor': 'rgb(255, 99, 132)',
                            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                            'tension': 0.1
                        },
                        {
                            'label': 'Cumulative Value',
                            'data': [],
                            'borderColor': 'rgb(54, 162, 235)',
                            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                            'tension': 0.1
                        }
                    ]
                },
                'bar_chart': {
                    'labels': [],
                    'datasets': [
                        {
                            'label': 'Investments',
                            'data': [],
                            'backgroundColor': 'rgba(75, 192, 192, 0.6)'
                        },
                        {
                            'label': 'Returns',
                            'data': [],
                            'backgroundColor': 'rgba(255, 99, 132, 0.6)'
                        }
                    ]
                },
                'area_chart': {
                    'labels': [],
                    'datasets': [
                        {
                            'label': 'Cumulative Investment',
                            'data': [],
                            'backgroundColor': 'rgba(75, 192, 192, 0.3)',
                            'borderColor': 'rgb(75, 192, 192)',
                            'fill': True
                        }
                    ]
                },
                'transaction_trends': {
                    'labels': [],
                    'datasets': []
                }
            }
            
            # Create a dictionary to store monthly data
            monthly_data = {}
            
            # Process monthly investments
            for item in monthly_investments:
                month_key = item['month'].strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'invested': Decimal('0.00'),
                        'returns': Decimal('0.00'),
                        'count': 0
                    }
                monthly_data[month_key]['invested'] += item['total_amount']
                monthly_data[month_key]['count'] += item['count']
            
            # Process monthly returns
            for item in monthly_returns:
                month_key = item['month'].strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'invested': Decimal('0.00'),
                        'returns': Decimal('0.00'),
                        'count': 0
                    }
                monthly_data[month_key]['returns'] += item['total_returns']
            
            # Sort months and build chart data
            sorted_months = sorted(monthly_data.keys())
            cumulative_value = Decimal('0.00')
            
            for month in sorted_months:
                data = monthly_data[month]
                cumulative_value += data['invested'] + data['returns']
                
                # Line chart data
                chart_data['line_chart']['labels'].append(month)
                chart_data['line_chart']['datasets'][0]['data'].append(float(data['invested']))
                chart_data['line_chart']['datasets'][1]['data'].append(float(data['returns']))
                chart_data['line_chart']['datasets'][2]['data'].append(float(cumulative_value))
                
                # Bar chart data
                chart_data['bar_chart']['labels'].append(month)
                chart_data['bar_chart']['datasets'][0]['data'].append(float(data['invested']))
                chart_data['bar_chart']['datasets'][1]['data'].append(float(data['returns']))
                
                # Area chart data
                chart_data['area_chart']['labels'].append(month)
                chart_data['area_chart']['datasets'][0]['data'].append(float(cumulative_value))
            
            # Process transaction trends
            transaction_types = ['deposit', 'withdrawal', 'investment', 'payment']
            transaction_colors = {
                'deposit': 'rgba(75, 192, 192, 0.6)',
                'withdrawal': 'rgba(255, 99, 132, 0.6)',
                'investment': 'rgba(54, 162, 235, 0.6)',
                'payment': 'rgba(255, 206, 86, 0.6)'
            }
            
            transaction_monthly = {}
            for item in monthly_transactions:
                month_key = item['month'].strftime('%Y-%m')
                trans_type = item['transaction_type']
                
                if month_key not in transaction_monthly:
                    transaction_monthly[month_key] = {}
                if trans_type not in transaction_monthly[month_key]:
                    transaction_monthly[month_key][trans_type] = Decimal('0.00')
                
                transaction_monthly[month_key][trans_type] += item['total_amount']
            
            # Build transaction trends datasets
            for trans_type in transaction_types:
                dataset = {
                    'label': trans_type.capitalize(),
                    'data': [],
                    'backgroundColor': transaction_colors.get(trans_type, 'rgba(153, 102, 255, 0.6)')
                }
                
                for month in sorted_months:
                    amount = float(transaction_monthly.get(month, {}).get(trans_type, Decimal('0.00')))
                    dataset['data'].append(amount)
                
                chart_data['transaction_trends']['datasets'].append(dataset)
            
            chart_data['transaction_trends']['labels'] = sorted_months
            
            # Calculate summary statistics
            total_invested = sum([float(monthly_data[m]['invested']) for m in sorted_months])
            total_returns = sum([float(monthly_data[m]['returns']) for m in sorted_months])
            total_investments = sum([monthly_data[m]['count'] for m in sorted_months])
            roi_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0
            
            summary = {
                'total_invested': round(total_invested, 2),
                'total_returns': round(total_returns, 2),
                'total_investments': total_investments,
                'roi_percentage': round(roi_percentage, 2),
                'period': f"{period} {period_type}(s)",
                'current_portfolio_value': round(float(cumulative_value), 2)
            }
            
            response_data = {
                'charts': chart_data,
                'summary': summary,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'type': period_type
                }
            }
            
            return enhance_response(
                data=response_data,
                message="Investment performance chart data retrieved successfully",
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            import traceback
            print(f"Error in InvestmentPerformanceChart: {str(e)}")
            print(traceback.format_exc())
            return enhance_response(
                data={},
                message=f"Error retrieving chart data: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PortfolioDistributionChart(BaseInvestorView, BaseValidator, generics.GenericAPIView):
    """
    API endpoint for Portfolio Distribution Chart Data
    Returns data for pie charts and donut charts showing:
    - Distribution by loan status
    - Distribution by loan purpose
    - Distribution by investment status
    """
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            # Get all investments for the user with related loan data
            investments = Investment.objects.filter(
                investor=user
            ).select_related('loan').prefetch_related('loan__loanrepaymentschedule_set')
            
            # Handle case where user has no investments
            if not investments.exists():
                # Return empty chart structure
                empty_chart = {
                    'labels': [],
                    'datasets': [{
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': '#ffffff',
                        'borderWidth': 2
                    }]
                }
                return enhance_response(
                    data={
                        'loan_status_distribution': {
                            'chart_data': empty_chart,
                            'summary': {'total_amount': 0, 'breakdown': {}}
                        },
                        'loan_purpose_distribution': {
                            'chart_data': empty_chart,
                            'summary': {'total_purposes': 0, 'breakdown': {}}
                        },
                        'investment_status_distribution': {
                            'chart_data': empty_chart,
                            'summary': {'breakdown': {}}
                        },
                        'roi_by_status': {},
                        'total_investments': 0,
                        'total_invested_amount': 0
                    },
                    message="Portfolio distribution chart data retrieved successfully (no investments found)",
                    status=status.HTTP_200_OK
                )
            
            # Distribution by Loan Status
            status_distribution = {}
            status_colors = {
                'pending': '#FF6384',
                'processing': '#36A2EB',
                'approved': '#4BC0C0',
                'repaid': '#9966FF',
                'defaulted': '#FF9F40'
            }
            
            # Distribution by Loan Purpose
            purpose_distribution = {}
            purpose_colors = [
                '#FF6384', '#36A2EB', '#4BC0C0', '#9966FF', '#FF9F40',
                '#FFCE56', '#C9CBCF', '#4BC0C0', '#FF6384', '#36A2EB'
            ]
            
            # Distribution by Investment Status
            investment_status_distribution = {
                'Open': {'amount': Decimal('0.00'), 'count': 0, 'color': '#36A2EB'},
                'closed': {'amount': Decimal('0.00'), 'count': 0, 'color': '#4BC0C0'}
            }
            
            # Process each investment
            for investment in investments:
                try:
                    loan = investment.loan
                    if not loan:
                        continue
                    
                    loan_status = loan.status or 'pending'
                    loan_purpose = loan.loan_purpose or 'Unspecified'
                    
                    # Handle investment status - can be None
                    investment_status = investment.status
                    if investment_status is None:
                        investment_status = 'Open'
                    elif isinstance(investment_status, str):
                        investment_status = investment_status.strip()
                        if not investment_status:
                            investment_status = 'Open'
                    else:
                        investment_status = str(investment_status)
                    
                    # Aggregate by loan status
                    if loan_status not in status_distribution:
                        status_distribution[loan_status] = {
                            'amount': Decimal('0.00'),
                            'count': 0,
                            'color': status_colors.get(loan_status, '#C9CBCF')
                        }
                    status_distribution[loan_status]['amount'] += investment.amount
                    status_distribution[loan_status]['count'] += 1
                    
                    # Aggregate by loan purpose
                    if loan_purpose not in purpose_distribution:
                        purpose_distribution[loan_purpose] = {
                            'amount': Decimal('0.00'),
                            'count': 0
                        }
                    purpose_distribution[loan_purpose]['amount'] += investment.amount
                    purpose_distribution[loan_purpose]['count'] += 1
                    
                    # Aggregate by investment status
                    status_key = 'closed' if investment_status.lower() == 'closed' else 'Open'
                    investment_status_distribution[status_key]['amount'] += investment.amount
                    investment_status_distribution[status_key]['count'] += 1
                except Exception as e:
                    # Skip investments with errors and continue processing
                    print(f"Error processing investment {investment.id}: {str(e)}")
                    continue
            
            # Build chart data for loan status distribution
            loan_status_chart = {
                'labels': [],
                'datasets': [{
                    'data': [],
                    'backgroundColor': [],
                    'borderColor': '#ffffff',
                    'borderWidth': 2
                }]
            }
            
            # Only add data if there are distributions
            if status_distribution:
                for loan_status_key, data in status_distribution.items():
                    if data['amount'] > 0:  # Only include non-zero amounts
                        loan_status_chart['labels'].append(loan_status_key.capitalize())
                        loan_status_chart['datasets'][0]['data'].append(float(data['amount']))
                        loan_status_chart['datasets'][0]['backgroundColor'].append(data['color'])
            
            # Build chart data for loan purpose distribution
            # Sort by amount and take top 10, filter out zero amounts
            sorted_purposes = sorted(
                [(p, d) for p, d in purpose_distribution.items() if d['amount'] > 0],
                key=lambda x: x[1]['amount'],
                reverse=True
            )[:10]
            
            loan_purpose_chart = {
                'labels': [],
                'datasets': [{
                    'data': [],
                    'backgroundColor': [],
                    'borderColor': '#ffffff',
                    'borderWidth': 2
                }]
            }
            
            for idx, (purpose, data) in enumerate(sorted_purposes):
                loan_purpose_chart['labels'].append(purpose)
                loan_purpose_chart['datasets'][0]['data'].append(float(data['amount']))
                loan_purpose_chart['datasets'][0]['backgroundColor'].append(
                    purpose_colors[idx % len(purpose_colors)]
                )
            
            # Build chart data for investment status distribution
            investment_status_chart = {
                'labels': [],
                'datasets': [{
                    'data': [],
                    'backgroundColor': [],
                    'borderColor': '#ffffff',
                    'borderWidth': 2
                }]
            }
            
            # Only add statuses with non-zero amounts
            for status_key, data in investment_status_distribution.items():
                if data['amount'] > 0:
                    investment_status_chart['labels'].append(status_key)
                    investment_status_chart['datasets'][0]['data'].append(float(data['amount']))
                    investment_status_chart['datasets'][0]['backgroundColor'].append(data['color'])
            
            # Calculate additional metrics
            total_invested = sum([float(data['amount']) for data in status_distribution.values()])
            
            # Get ROI by loan status
            roi_by_status = {}
            for investment in investments:
                try:
                    if not investment.loan:
                        continue
                    loan_status = investment.loan.status or 'pending'
                    if loan_status not in roi_by_status:
                        roi_by_status[loan_status] = {
                            'invested': Decimal('0.00'),
                            'returns': Decimal('0.00')
                        }
                    roi_by_status[loan_status]['invested'] += investment.amount
                    if investment.net_return:
                        roi_by_status[loan_status]['returns'] += investment.net_return
                except Exception as e:
                    print(f"Error calculating ROI for investment {investment.id}: {str(e)}")
                    continue
            
            # Calculate ROI percentages
            roi_data = {}
            for status_key, data in roi_by_status.items():
                invested = float(data['invested'])
                returns = float(data['returns'])
                roi_percentage = (returns / invested * 100) if invested > 0 else 0
                roi_data[status_key] = {
                    'invested': round(invested, 2),
                    'returns': round(returns, 2),
                    'roi_percentage': round(roi_percentage, 2)
                }
            
            response_data = {
                'loan_status_distribution': {
                    'chart_data': loan_status_chart,
                    'summary': {
                        'total_amount': round(total_invested, 2),
                        'breakdown': {
                            status_key: {
                                'amount': round(float(data['amount']), 2),
                                'count': data['count'],
                                'percentage': round((float(data['amount']) / total_invested * 100) if total_invested > 0 else 0, 2)
                            }
                            for status_key, data in status_distribution.items()
                        }
                    }
                },
                'loan_purpose_distribution': {
                    'chart_data': loan_purpose_chart,
                    'summary': {
                        'total_purposes': len(sorted_purposes),
                        'breakdown': {
                            purpose: {
                                'amount': round(float(data['amount']), 2),
                                'count': data['count'],
                                'percentage': round((float(data['amount']) / total_invested * 100) if total_invested > 0 else 0, 2)
                            }
                            for purpose, data in sorted_purposes
                        }
                    }
                },
                'investment_status_distribution': {
                    'chart_data': investment_status_chart,
                    'summary': {
                        'breakdown': {
                            status_key: {
                                'amount': round(float(data['amount']), 2),
                                'count': data['count'],
                                'percentage': round((float(data['amount']) / total_invested * 100) if total_invested > 0 else 0, 2)
                            }
                            for status_key, data in investment_status_distribution.items()
                        }
                    }
                },
                'roi_by_status': roi_data,
                'total_investments': investments.count(),
                'total_invested_amount': round(total_invested, 2)
            }
            
            return enhance_response(
                data=response_data,
                message="Portfolio distribution chart data retrieved successfully",
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            import traceback
            print(f"Error in PortfolioDistributionChart: {str(e)}")
            print(traceback.format_exc())
            return enhance_response(
                data={},
                message=f"Error retrieving distribution chart data: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

