from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from products.models import ProductCategory, Product


def index(request):
    return render(request, 'products/index.html')


def products(request, category_id=None, page_number=1):
    products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
    print(products)
    per_page = 3    #количество товаров
    sorted_queryset = products.order_by('id') #сортировка продуктов
    paginator = Paginator(sorted_queryset, per_page) #Класс принимает два аргумента object_list (список который нужно
                                                     # пагинировать, per_page количество отобр товаров)
    product_paginator = paginator.page(page_number) #передается номер страницы которою мы отображаем на экране
    #product_paginator это тот же самый квери сет что и products, только у него реализованы разширеные методы пагинации

    context = {'products': product_paginator,
               'category_id': category_id,
               'categories': ProductCategory.objects.all()}
    return render(request, 'products/products.html', context)












