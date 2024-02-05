from django.db import models
import stripe
from django.conf import settings

# Create your models here.

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductCategory(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    #создаем продукты:
    name = models.CharField(max_length=150)
    descriptions = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    # количество товаров, PositiveIntegerField - обозначает, что всегда положительное
    quantity = models.PositiveIntegerField(default=0)
    img = models.ImageField(upload_to='products_img')
    stripe_product_price_id = models.CharField(max_length=128, null=True, blank=True)
    category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
    #связь между моделями. models.CASCADE - если удаляем категорию, то все характеристики(продукты) удаляются

    # Что бы не вызывать сохранения цены для каждого обьекта мы сделали метод который в каждом товаре сохраняет
    # его цену в stripe.Это метод который сохраняет обьекты в базе данных она срабатывает при сохранении
    # обьектов в базе данных и до вызова метода super у нас срабатывает логика добавления id stripe к товару

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.stripe_product_price_id:
            stripe_product_price_id = self.create_stripe_product_price()
            self.stripe_product_price_id = stripe_product_price_id['id']
        return super(Product, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    # Создание самого продукта и цены в stripe cabinet
    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.name)
        stripe_product_price = stripe.Price.create(
            product=stripe_product['id'], unit_amount=round(self.price * 100), currency='pln'
        )
        return stripe_product_price

    def __str__(self):
        return f'Продукт {self.name}, Категория {self.category}'
