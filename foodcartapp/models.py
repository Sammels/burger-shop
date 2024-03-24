from django.db import models
from django.db.models import QuerySet, Prefetch, Sum, Count, F
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = PhoneNumberField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

class OrderQuerySet(models.QuerySet):
    def orders_with_total_cost_and_prefetched_products(self):
        return self.prefetch_related(
            Prefetch(
                'products',
                queryset=OrderItem.objects.select_related('product'),
            )).annotate(
            total_cost=Sum(F('products__product__price') * F('products__quantity'))
            ).all()

class Order(models.Model):
    address = models.TextField(verbose_name="Место доставки")
    firstname = models.CharField(max_length=50, verbose_name="Имя")
    lastname = models.CharField(max_length=50, verbose_name="Фамилия")
    phonenumber = PhoneNumberField(max_length=128, region="RU")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)

    class Meta:
        verbose_name = "Заказ"

        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.firstname}: {self.lastname} - {self.address}"

    objects = OrderQuerySet.as_manager()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="products", verbose_name="заказ", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", verbose_name="продукт", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="количество", default=1)

    class Meta:
        verbose_name = "пункт заказа"
        verbose_name_plural = "пункты заказа"
        unique_together = [
            ["order", "product"]
        ]

    def __str__(self):
        return f"{self.order.pk}: {self.product.name} - {self.quantity}"


