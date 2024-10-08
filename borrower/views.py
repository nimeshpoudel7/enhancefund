from lib2to3.fixes.fix_input import context

import pdfplumber
from django.shortcuts import render
import io

from borrower.credit_utils import load_and_preprocess_data, calculate_risk_score
from borrower.models import Borrower, CreditScoreHistory
from borrower.serializer import CreditScoreHistorySerializer, BorrowerSerializer
from enhancefund.Constant import REQUIRED_CREATE_LOAN_FIELD
from enhancefund.postvalidators import BaseValidator
from enhancefund.rolebasedauth import BaseInvestorView, BaseBorrowerView
from rest_framework import generics

from enhancefund.utils import enhance_response, create_payment_link_for_customer, check_Add_fund_status, format_details
from investor.models import InvestorBalance
from investor.serializers import PaymentHistorySerializer, TransactionSerializer, InvestorBalanceSerializer
from loans.models import PaymentHistory, Transaction
from users.models import User
from rest_framework import status
from decimal import Decimal


class CreditStatementAnalysis(BaseBorrowerView,BaseValidator,generics.GenericAPIView):
    def post(self, request, *args, **kwargs):

        if 'file' not in request.FILES:
            return enhance_response(
                data={},
                status=status.HTTP_400_BAD_REQUEST,
                message="No file is selected"
            )

        file = request.FILES['file']
        if file.name == '':
            return enhance_response(
                data={},
                status=status.HTTP_400_BAD_REQUEST,
                message="No selected file"
            )

        if not file.name.endswith('.pdf'):
            return enhance_response(
                data={},
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid file type"
            )

        try:
            # Read the PDF content into memory
            file_contents = file.read()
            if len(file_contents) == 0:
                return enhance_response(
                    data={},
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Uploaded file is empty"
                )

            file_like_object = io.BytesIO(file_contents)

            # Check if the PDF file has pages
            with pdfplumber.open(file_like_object) as pdf:
                if len(pdf.pages) == 0:
                    return enhance_response(
                        data={},
                        status=status.HTTP_400_BAD_REQUEST,
                        message="PDF file has no pages"
                    )

            file_like_object.seek(0)
            # Process the file
            features, statement_start_date, statement_end_date = load_and_preprocess_data(file_like_object)

            risk_score = calculate_risk_score(features)
            # insert into db credit history
            user = request.user
            user_id = User.objects.get(email=user.email)
            borrower_id = Borrower.objects.get(user=user)


            flattened_details = {key: list(inner_dict.values())[0] for key, inner_dict in features.to_dict().items()}

            keys_to_remove = ['large_purchase_frequency', 'recurring_transactions','transaction_frequency','total_spending']
            for key in keys_to_remove:
                flattened_details.pop(key, None)  # or use del details[key]

            flattened_details['statement_start_date']=statement_start_date.strftime('%Y-%m-%d')
            flattened_details['statement_end_date']=statement_end_date.strftime('%Y-%m-%d')
            flattened_details['risk_score']=risk_score
            # Add the transformed details back to the data
            print(flattened_details)
            # if user_credit_history is None:
            serializer = CreditScoreHistorySerializer(data=flattened_details,context={"borrower": borrower_id})
            if serializer.is_valid():
                serializer.save()
                user.checklist = ['CREDIT_STATEMENT']  # Add 'BANK_ACCOUNT' to the user's checklist
                user.save()  # Ensure changes to user checklist are saved
                return enhance_response(
                    data=serializer.data,
                    status=status.HTTP_200_OK,
                    message="Successfully processed file"
                )
            else:
                print(serializer.errors)
                return enhance_response(
                    data={},
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Unable to proceed file"
                    )




        except Exception as e:
            return enhance_response(
                data={},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Error processing file: {str(e)}"
            )

class CreateBorrower(BaseBorrowerView, BaseValidator, generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        validation_errors = self.validate_data(request.data, REQUIRED_CREATE_LOAN_FIELD)
        if validation_errors:
            return enhance_response(data=validation_errors, status=status.HTTP_400_BAD_REQUEST,
                                    message="Please enter required fields")
        user = request.user
        user_id = User.objects.get(email=user.email)
        borrowerDetails = Borrower.objects.filter(user=user_id).first()
        if borrowerDetails is not None:
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="You have already borrower account")

        data_to_send={
            "bank_statement_url":"null",
            "employment_status":request.data.get("employment_status"),
            "annual_income": request.data.get("annual_income"),
            "account_balance":0
        }
        serializer = BorrowerSerializer(data=data_to_send, context={"user": user_id})
        if serializer.is_valid():
            serializer.save()
        else:
            return enhance_response(data={}, status=status.HTTP_400_BAD_REQUEST,
                                    message="Invalid data")


        # CALCULATE INTEREST RATE AND ALSO HOW MUCH THE BORROWER WILL PAY ACC. TO TERM MONTHS
        return enhance_response(data={}, status=status.HTTP_200_OK,
                                    message="Your loan is created successfully")