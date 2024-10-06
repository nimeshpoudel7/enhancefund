from enhancefund.commonserializer import CommonSerializer
from investor.models import InvestorBalance
from loans.models import PaymentHistory, Transaction


class PaymentHistorySerializer(CommonSerializer):
    class Meta:
        model = PaymentHistory
        fields = ['stripe_payment_id', 'payment_amount']

    def create(self, validated_data):
        # Retrieve the user from context
        user = self.context.get('user')

        if not user:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return PaymentHistory.objects.create(user=user, **validated_data)


class TransactionSerializer(CommonSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount','url','payment_id']

    def create(self, validated_data):
        # Retrieve the user from context
        user = self.context.get('user')

        if not user:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return Transaction.objects.create(user=user, **validated_data)

class InvestorBalanceSerializer(CommonSerializer):
    class Meta:
        model = InvestorBalance
        fields = ['account_balance']

    def create(self, validated_data):
        # Retrieve the user from context
        user = self.context.get('user')

        if not user:
            raise CommonSerializer.ValidationError("User not found in context")

        # Create the address and associate it with the user
        return InvestorBalance.objects.create(user=user, **validated_data)
    def update(self, instance, validated_data):
        # Update the address instance
        instance.account_balance = validated_data.get('account_balance', instance.account_balance)
        instance.save()
        return instance