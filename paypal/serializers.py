from rest_framework import serializers
from paypal.models import DeliveryDetails

class PaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    payer_id = serializers.CharField()

class DeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDetails
        fields = '__all__'
