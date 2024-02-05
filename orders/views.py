from http import HTTPStatus
import stripe
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from orders.forms import OrderCreateForm
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from cart.user_cart import Cart
from django.conf import settings
from products.models import Product

from orders.models import Order

import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessTemplateView(TemplateView):
    template_name = 'orders/success.html'


class CancelledTemplateView(TemplateView):
    template_name = 'orders/cancelled.html'


class OrderCreateView(CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderCreateForm
    success_url = reverse_lazy('orders:order_created')

    #     #создается сессия для оформления заказа с использованием Stripe Checkout
    #     return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)
    #     #Здесь происходит перенаправление пользователя на URL, который предоставляется объектом checkout_session
    #     #HTTPStatus.SEE_OTHER указывает на использование статуса 303 See Other, который сообщает браузеру выполнить
    #     # GET запрос по указанному URL.

    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        # print(f'$$${self.request.user, request}')
        baskets = self.request.user.cart  # Наша текущая корзина у определенного юзера
        print(f'$$$$ {baskets}')
        line_items = []  # Сюда будем помещать каждый товар
        for basket in baskets:
            # print(Product.objects.get(id=int(basket))) # Возвращает Строку
            # print(Product.objects.filter(id=int(basket))) # Возраст QuerySet
            item = {
                'price': Product.objects.get(id=int(basket)).stripe_product_price_id,
                'quantity': baskets[basket]['quantity']
            }
            line_items.append(item)
            # print(line_items)
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            metadata={'order_id': self.object.id},
            mode='payment',
            success_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order-success')),
            cancel_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order-cancelled')),
        )
        return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context['cart'] = cart
        print(context['cart'])
        return context

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super(OrderCreateView, self).form_valid(form)


@csrf_exempt
#Это декоратор, который освобождает представление от защиты CSRF.
# CSRF — это функция безопасности в веб-приложениях, позволяющая
# предотвратить несанкционированные запросы.
def my_webhook_view(request):
    #функция обрабатывает веб хуки
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    # print(repr(payload))

#     #получаем тело запроса, содержащее данные веб-хука, и сохраняем его в переменной payload
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     #извлекаем значение заголовка HTTP_STRIPE_SIGNATURE из метаданных запроса и сохраняет его в переменной sig_header
#     event = None
#     #Здесь будет сохранен объект события Stripe после его проверки.
#
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    #блок try-except проверяет подписи веб-хука. Если подпись не верна или есть проблемы с данными,
    # будет возвращен HTTP-ответ со статусом 400 Bad Request.

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        fulfill_order(session)
    #Если тип события Stripe равен 'checkout.session.completed', это означает успешное завершение сеанса
    # оформления заказа. В таком случае вызывается функция fulfill_order, передавая ей объект сеанса.

    return HttpResponse(status=200)
     # статус 200 указывает, что веб-хук успешно обработан.


#Это функция с которой мы достаем уже сессию payload и передаем в функцию ее
  # 1. В product.models мы создадим метод de_json этот метод будет возвращать словарь с данными о корзине
def fulfill_order(session):
    try:
        order_id = int(session.metadata.get('order_id', 0))
        order = Order.objects.filter(id=order_id).first()
        print(order)
        if order:
            order.update_after_payment()
            return f'This order id {order_id}'
        else:
            return f'Order with id {order_id} not found.'
    except Exception as e:
        logger.exception(f'Error processing order: {e}')


class OrderUserLookTemplateView(View):
    template_name = 'orders/orders.html'

    def get_queryset(self):
        return Order.objects.filter(initiator=self.request.user)

    def get(self, request):
        queryset = self.get_queryset()
        context = {
            'orders': queryset,
        }
        return render(request, self.template_name, context)





