from django.urls import path
from cart.views import add_to_cart, remove_from_cart, cart_upd_data


app_name = 'cart'

urlpatterns = [
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart_upd_data', cart_upd_data, name='cart_upd_data'),
]
