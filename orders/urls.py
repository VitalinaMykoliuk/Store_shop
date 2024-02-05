from django.urls import path
from orders.views import OrderCreateView, SuccessTemplateView, CancelledTemplateView, OrderUserLookTemplateView


app_name = 'orders'

urlpatterns = [
    path('order-created/', OrderCreateView.as_view(), name='order_created'),
    path('order-success/', SuccessTemplateView.as_view(), name='order-success'),
    path('order-cancelled/', CancelledTemplateView.as_view(), name='order-cancelled'),
    path('order/', OrderUserLookTemplateView.as_view(), name='order_main'),

]