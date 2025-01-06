from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import paypalrestsdk
from django.conf import settings
from history.models import Order, OrderItem
from products.models import Product
from users.models import CustomUser

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        total_value = request.data.get('total_value')
        return_url = request.data.get('return_url')
        cancel_url = request.data.get('cancel_url')

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(total_value),
                    "currency": "PLN"
                },
                "description": "Payment for order"
            }],
            "redirect_urls": {
                "return_url": str(return_url),
                "cancel_url": str(cancel_url)
            }
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return Response({'approval_url': approval_url}, status=status.HTTP_200_OK)

        return Response({'error': 'Payment creation failed'}, status=status.HTTP_400_BAD_REQUEST)


class ExecutePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_pk = request.data.get('user_pk')
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')
        order_items = request.data.get('order_items')
        user = CustomUser.objects.get(pk=user_pk)

        try:
            payment = paypalrestsdk.Payment.find(payment_id)
        except paypalrestsdk.ResourceNotFound:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        if payment.execute({"payer_id": payer_id}):
            total_amount = 0
            order = Order.objects.create(
                user=user,
                status='pending',
                transaction_id=payment.id
            )

            for item in order_items:
                product = Product.objects.get(id=item['product_id'])
                total_amount += product.price * item['quantity']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_purchase=product.price
                )

            return Response({'message': 'Payment executed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment execution failed'}, status=status.HTTP_400_BAD_REQUEST)


class CancelPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'message': 'Payment cancelled by the user'}, status=status.HTTP_200_OK)
