from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from cart.user_cart import Cart
from django.urls import reverse


def add_to_cart(request, product_id):
    # Получаем товар из базы данных
    product = get_object_or_404(Product, id=product_id)
    # Инициализируем корзину
    cart = Cart(request)
    # Добавляем выбранный товар в корзину
    cart.add_product(product)
    print(cart)
    # Можете также передавать дополнительные параметры, такие как количество:
    cart.save()
    # Возвращаем ответ в формате JSON
    # return JsonResponse({'message': 'Товар успешно добавлен в корзину'})
    return redirect(reverse('products:index'))


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    # Удаляем выбранный товар из корзины
    cart.remove(product)
    cart.save()
    return redirect(reverse('users:profile'))


def cart_upd_data(request):
    quantity = request.GET['quantity']
    product_id = int(request.GET['product_id'])
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add_product(product, quantity=quantity, update_quantity=True)
    cart.save()
    return JsonResponse({'caff': 'caff'})







