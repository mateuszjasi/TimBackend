from django.urls import path
from history.views import OrderList, OrderDetail, UserOrderList

urlpatterns = [
    path('orders/', OrderList.as_view(), name='orders-list'),
    path('orders/<int:pk>/', UserOrderList.as_view(), name='user-orders-list'),
    path('orders/<int:pk>/<int:pk2>/', OrderDetail.as_view(), name='order-detail'),
]
