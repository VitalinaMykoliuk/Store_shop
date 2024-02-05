from django.urls import path
from products.views import products


app_name = 'products'
urlpatterns = [
    path('products', products, name='index'),
    path('category/<int:category_id>/page/<int:page_number>/', products, name='category'),
    path('page/<int:page_number>/', products, name='paginator'),
]


