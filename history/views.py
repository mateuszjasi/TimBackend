from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsStaff
from users.views import User
from .models import Order
from .serializers import OrderSerializer

class OrderList(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class UserOrderList(APIView):
    def get(self, request, pk):
        if request.user.pk != pk and not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            order = Order.objects.get(user=User.objects.get(pk=pk))
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class OrderDetail(APIView):
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsStaff()]
        return []

    def get(self, request, pk, pk2):
        if request.user.pk != pk and not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            order = Order.objects.get(pk=pk2)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk, pk2):
        try:
            order = Order.objects.get(pk=pk2)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if order.status == 'pending':
            order.status = 'completed'
            order.save()
            return Response({'message': 'Order status updated to completed.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Order status is not pending, cannot change to completed.'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, pk2):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
