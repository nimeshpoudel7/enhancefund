from borrower.serializer import BorrowerSerializer, CreditScoreHistorySerializer
from enhancefund.commonserializer import CommonSerializer
from loans.models import Loan, LoanRepaymentSchedule, Investment, EMIPayment


class LoanSerializer(CommonSerializer):
    borrower = BorrowerSerializer()

    class Meta:
        model = Loan
        fields = ['id','amount','term_months','status','loan_purpose','interest_rate','total_payable','is_fulfill','loan_amount','borrower']

    def create(self, validated_data):
        # Retrieve the user from context
        borrower = self.context.get('borrower')


        if not borrower:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return Loan.objects.create(borrower=borrower, **validated_data)


class SchedulerSerializer(CommonSerializer):
    class Meta:
        model = LoanRepaymentSchedule
        fields = ['installment_number','due_date','payment_status','amount_paid','amount_due']

    def create(self, validated_data):
        # Retrieve the user from context
        loan = self.context.get('loan')


        if not loan:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return LoanRepaymentSchedule.objects.create(loan=loan, **validated_data)
class InvestmentSerializer(CommonSerializer):
    class Meta:
        model = Investment
        fields = ['loan', 'investor', 'amount', 'created_at','net_return','closed_at']
        read_only_fields = ['created_at', 'investor']  # Make investor read-only

    def create(self, validated_data):
        # Retrieve the loan and investor from the context
        loan = self.context.get('loan')
        investor = self.context.get('investor')

        # Ensure that both loan and investor are provided
        if not loan or not investor:
            raise CommonSerializer.ValidationError("Loan and investor must be provided in the context.")

        investment = Investment.objects.create(
            loan=loan,
            investor=investor,
            net_return=validated_data['net_return'],
            amount=validated_data['amount'],
            closed_at = validated_data['closed_at']

        )
        return investment


class EmiSerializer(CommonSerializer):
    class Meta:
        model = EMIPayment
        fields = ['stripe_payment_id','amount','payment_date','status']

    def create(self, validated_data):
        # Retrieve the user from context
        loan = self.context.get('loan')


        if not loan:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return EMIPayment.objects.create(loan=loan, **validated_data)