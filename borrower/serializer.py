from borrower.models import CreditScoreHistory, Borrower
from enhancefund.commonserializer import CommonSerializer


class CreditScoreHistorySerializer(CommonSerializer):
    class Meta:
        model = CreditScoreHistory
        fields = ['risk_score','average_transaction','average_transaction','payment_consistency','date_recorded','statement_start_date','statement_end_date','credit_utilization']

    def create(self, validated_data):
        # Retrieve the user from context
        borrower = self.context.get('borrower')

        if not borrower:
            raise CommonSerializer.ValidationError("borrower not found in context")

        # Create the address and associate it with the user
        return CreditScoreHistory.objects.create(borrower=borrower, **validated_data)
    def update(self, instance, validated_data):
        # Update the address instance
        instance.risk_score = validated_data.get('risk_score', instance.risk_score)
        instance.average_transaction = validated_data.get('average_transaction', instance.average_transaction)
        instance.payment_consistency = validated_data.get('payment_consistency', instance.payment_consistency)
        instance.date_recorded = validated_data.get('date_recorded', instance.date_recorded)

        instance.credit_utilization = validated_data.get('credit_utilization', instance.credit_utilization)
        instance.statement_end_date = validated_data.get('statement_end_date', instance.statement_end_date)
        instance.statement_start_date = validated_data.get('statement_start_date', instance.statement_start_date)

        instance.save()
        return instance


class BorrowerSerializer(CommonSerializer):
    class Meta:
        model = Borrower
        fields = ['annual_income', 'employment_status','account_balance']

    def create(self, validated_data):
        # Retrieve the user from context
        user = self.context.get('user')


        if not user:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return Borrower.objects.create(user=user, **validated_data)
