from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import paypalrestsdk
from django.conf import settings
from history.models import Order, OrderItem
from paypal.models import DeliveryDetails
from products.models import Product
from urllib.parse import urlencode

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return_url = request.data.get('return_url')
        cancel_url = request.data.get('cancel_url')
        order_items = request.data.get('order_items', [])
        delivery_details_data = request.data.get('deliveryDetails', None)
        user = request.user

        order = Order.objects.create(
            user=user,
            status='unpaid',
        )

        if delivery_details_data:
            DeliveryDetails.objects.create(
                order=order,
                name=delivery_details_data.get('name', ''),
                street=delivery_details_data.get('street', ''),
                house_number=delivery_details_data.get('houseNumber', ''),
                city=delivery_details_data.get('city', ''),
                postal_code=delivery_details_data.get('postalCode', ''),
                phone_number=delivery_details_data.get('phoneNumber', ''),
            )

        total_value = 0
        for item in order_items:
            try:
                quantity = item['quantity']
                product_id = item['id']
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                order.delete()
                return Response({'error': f"Product with id {item['id']} does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)

            if product.stock < quantity:
                order.delete()
                return Response({'error': f"Not enough stock for product {product.name}."},
                                status=status.HTTP_400_BAD_REQUEST)

            total_value += product.price * quantity
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )

        query_params = urlencode({'order_id': order.id})
        cancel_url_with_params = f"{cancel_url}?{query_params}"

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": f"{total_value:.2f}",
                    "currency": "PLN"
                },
                "description": f"Payment for order {order.id}"
            }],
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url_with_params
            }
        })

        if payment.create():
            order.transaction_id = payment.id
            order.save()
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return Response({'approval_url': approval_url}, status=status.HTTP_200_OK)

        order.delete()
        return Response({'error': 'Payment creation failed'}, status=status.HTTP_400_BAD_REQUEST)


class ExecutePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')

        try:
            payment = paypalrestsdk.Payment.find(payment_id)
        except paypalrestsdk.ResourceNotFound:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        if payment.execute({"payer_id": payer_id}):
            try:
                order = Order.objects.get(transaction_id=payment_id)
            except Order.DoesNotExist:
                return Response({'error': 'Order associated with this payment not found.'}, status=status.HTTP_404_NOT_FOUND)
            if DeliveryDetails.objects.filter(order=order).exists():
                order.status = 'shipping'
            else:
                order.status = 'paid'
            order.save()

            order_items = OrderItem.objects.select_related('product').filter(order=order)
            for item in order_items:
                product = item.product
                product.stock -= item.quantity
                product.save()

            return Response({'message': 'Payment executed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment execution failed'}, status=status.HTTP_400_BAD_REQUEST)

class CancelPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        user = request.user

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status == 'paid':
            return Response({'message': 'Cannot cancel a paid order.'}, status=status.HTTP_400_BAD_REQUEST)

        if order.status == 'unpaid':
            order.status = 'cancelled'
            order.save()
            return Response({'message': 'Payment cancelled and order status updated.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Order already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
