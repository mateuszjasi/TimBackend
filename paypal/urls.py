from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreatePaymentView.as_view(), name='create_payment'),
    path('execute/', views.ExecutePaymentView.as_view(), name='execute_payment'),
    path('cancel/', views.CancelPaymentView.as_view(), name='cancel_payment'),
]
