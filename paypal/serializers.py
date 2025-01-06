from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    payer_id = serializers.CharField()
