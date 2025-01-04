from django.urls import path
from history.views import OrderList, OrderDetail

urlpatterns = [
    path('orders/', OrderList.as_view(), name='orders-list'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
]
