from django.urls import path
from history.views import *

urlpatterns = [
    path('orders/', OrderList.as_view(), name='orders-list'),
    path('orders/<int:pk>/', UserOrderList.as_view(), name='user-orders-list'),
    path('orders/ready/', OrderReadyList.as_view(), name='order-ready-list'),
    path('orders/ready/<int:pk>/', OrderReady.as_view(), name='order-ready'),
    path('orders/pickup/', OrderPickupList.as_view(), name='order-pickup-list'),
    path('orders/pickup/<int:pk>/', OrderPickup.as_view(), name='order-pickup'),
    path('orders/delivery/', OrderDeliveryList.as_view(), name='order-delivery'),
    path('orders/delivery/<int:pk>/', OrderDelivery.as_view(), name='order-delivered'),
]
