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
        orders = Order.objects.all().order_by('-pk')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class UserOrderList(APIView):
    def get(self, request, pk):
        if pk == 0 or request.user.pk == pk or request.user.is_staff:
            try:
                if pk == 0:
                    pk = request.user.id
                order = Order.objects.filter(user=User.objects.get(pk=pk)).order_by('-pk')
                serializer = OrderSerializer(order, many=True)
                return Response(serializer.data)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class OrderReadyList(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        orders = Order.objects.filter(status='paid').order_by('-pk')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderReady(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if order.status == 'paid':
            order.status = 'ready'
            order.save()
            return Response({'message': 'Order status updated to ready.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Order status is not paid, cannot change to ready.'}, status=status.HTTP_400_BAD_REQUEST)

class OrderPickupList(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        orders = Order.objects.filter(status='ready').order_by('-pk')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderPickup(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if order.status == 'ready':
            order.status = 'completed'
            order.save()
            return Response({'message': 'Order status updated to completed.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Order status is not ready, cannot change to completed.'}, status=status.HTTP_400_BAD_REQUEST)

class OrderDeliveryList(APIView):

    def get(self, request):
        orders = Order.objects.filter(status='shipping').order_by('-pk')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderDelivery(APIView):

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if order.status == 'shipping':
            order.status = 'completed'
            order.save()
            return Response({'message': 'Order status updated to completed.'}, status=status.HTTP_200_OK)

        return Response({'error': 'Order status is not shipping, cannot change to completed.'},
                        status=status.HTTP_400_BAD_REQUEST)