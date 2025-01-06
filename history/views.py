from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsStaff
from .models import Order
from .serializers import OrderSerializer

class OrderList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderDetail(APIView):
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsStaff()]
        return [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if order.status == 'pending':
            order.status = 'completed'
            order.save()
            return Response({'message': 'Order status updated to completed.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Order status is not pending, cannot change to completed.'}, status=status.HTTP_400_BAD_REQUEST)
