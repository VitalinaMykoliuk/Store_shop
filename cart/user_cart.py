from decimal import Decimal
from django.conf import settings
from django.http import request

from products.models import Product
from users.models import User


class Cart(object):

    def __init__(self, request):
        """Инициализируем корзину"""
        self.request = request
        # инициализация корзины с помощью объекта request
        if self.request.user.is_authenticated:
            self.cart = self.request.user.cart
            if not self.cart:
                self.cart = {}
        else:
            self.session = request.session  # храним текущую сессию с
            # помощью чтобы сделать его доступным для других методов класса
            self.cart = self.session.get(settings.CART_SESSION_ID, {})  #пытаемся получить корзину с текущей сессии с помощью

        # Если в сессии отсутствует корзина,
        # то создать сессию с пустой корзиной, установив пустой словарь в сессии

        # Мы ожидаем, что наш словарь корзины будет использовать коды продуктов в качестве ключей и словарь
        # с количеством и ценой в качестве значения для каждого ключа.
        # Таким образом, мы можем гарантировать, что продукт не будет добавлен в корзину более одного раза;
        # можно также упростить доступ к данным элементов корзины.

    def add_product(self, product, quantity=1, update_quantity=False):
        # product : Экземпляр Product для добавления или обновления в корзине
        # quantity : Необязательное целое число для количества продукта
        # update_quantity : Это логическое значение, которое указывает, требуется ли обновление количества
        # с заданным количеством (True), или же новое количество должно
        # быть добавлено к существующему количеству (False)

        """Добавляем продукт в корзину или обновляем его количество."""
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': int(product.price)}
            # price : str(product.price) Цена продукта преобразуется из десятичного разделителя в строку,
            # чтобы сериализовать его
        if update_quantity:
            self.cart[product_id]['quantity'] = int(quantity)
        else:
            self.cart[product_id]['quantity'] += int(quantity)
        print(self.cart)

    def has_items(self):
        """Проверка наличия товаров в корзине."""
        return bool(self.cart)   # Проверка, есть ли какие-либо товары в корзине

    def get_cart_content(self):
        return list(self.cart.values())

    def get_cart_content_count(self):
        return len(list(self.cart.values()))

    def save(self):
        if self.request.user.is_authenticated:
            user_= User.objects.get(id=self.request.user.id)
            user_.cart = self.cart
            user_.save()
        else:
            # Обновление сессии cart
            self.session[settings.CART_SESSION_ID] = self.cart
            # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
            # self.session.modified = True
            self.session.save()
            """Метод save() сохраняет все изменения в корзине в сессии и помечает сессию как 
               modified с помощью session.modified = True. Это говорит о том, 
               что сессия modified и должна быть сохранена"""

    def remove(self, product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            # метод save() для обновления корзины в сессии

    def __iter__(self):
        """Перебор элементов в корзине и получение продуктов из базы данных."""

        # извлекаем экземпляры продукта, присутствующие в корзине
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            # item представляет собой словарь, содержащий информацию о товаре
            # item['price'] = Decimal(item['price']) конвертирует значение цены товара в тип данных Decimal.
            # Это может быть сделано для обработки десятичных значений с большей точностью, чем с плавающей запятой
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            # item['total_price'] = item['price'] * item['quantity'] вычисляю
            # общую стоимость товара, умножая цену на количество, и сохраняю
            # результат в ключе 'total_price' в словаре item
            yield item
            # yield используемый вместо return, превращает функцию в генератор,
            # возвращает значение при каждой итерации цикла и сохраняет состояние функции
            # Это позволяет приостанавливать выполнение функции и возвращать промежуточные
            # результаты без полного завершения функции
            # В то время как используется для возврата значения из функции и завершения её выполнения.
            # Когда встречается оператор return, функция возвращает указанное значение и завершает свою работу
            #  если нам нужно что бы функция что то выдавала и продолжала
            #  работать а не останавливалась то используем yield

    def __len__(self):
        """Подсчет всех товаров в корзине."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Подсчет стоимости товаров в корзине."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Метод для очистки сеанса корзины"""
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        # удаляет элемент корзины из сессии
        # self.session.modified = True
        self.session.save()
        #  устанавливает флаг modified сессии в True.
        #  Это сообщает фреймворку, что сессия была изменена и нуждается в сохранении


