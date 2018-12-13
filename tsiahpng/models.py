from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
import django.contrib.auth.models

from . import utils


class Shop(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    priority = models.IntegerField(default=0, db_index=True)

    image = models.ImageField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = None
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def products(self):
        return Product.objects.filter(shop=self)


class Category(models.Model):
    """Categories of the products
    """
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, models.CASCADE, db_index=True)

    priority = models.IntegerField(default=0, db_index=True)

    name = models.CharField(max_length=256)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return self.name


class Product(models.Model):
    """The products for sale
    """
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, models.CASCADE, db_index=True)
    category = models.ForeignKey(
        Category, models.SET_NULL, db_index=True, null=True, blank=True)

    priority = models.IntegerField(default=0, db_index=True)

    name = models.CharField(max_length=256)
    price = models.PositiveIntegerField()

    class Meta:
        ordering = ['shop', 'category', '-priority']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.category:
            self.category = None
        super().save(*args, **kwargs)


class Order(models.Model):
    """An exact order that would send to the shop owner, collect all the
    tickets from every user
    """
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, models.SET_NULL, null=True)

    order_date = models.DateField(
        default=utils.order_date_default, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    alias = models.CharField(max_length=256, blank=True, null=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-order_date', 'create_time']

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = None
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.alias:
            return self.alias
        else:
            return _(
                'Order from {shop} (created on {time:%Y/%m/%d %H:%M})').format(
                    shop=self.shop,
                    time=timezone.localtime(self.create_time),
                )

    @property
    def order_date_short(self) -> str:
        today = timezone.localtime().date()

        if self.order_date == today:
            return _('Today')
        elif self.order_date + timezone.timedelta(1) == today:
            return _('Yesterday')
        elif self.order_date - timezone.timedelta(1) == today:
            return _('Tomorrow')
        else:
            return self.order_date.strftime('%m/%d')

    def tickets(self, **kwargs):
        return Ticket.objects.filter(order=self, **kwargs)

    def total_price(self):
        sum_price = self.tickets().aggregate(val=models.Sum('price'))['val']
        if not sum_price:
            return 0
        return sum_price


class Ticket(models.Model):
    """A ticket recorded the detail of the item that people ordered
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, models.CASCADE, db_index=True)
    user = models.ForeignKey(
        django.contrib.auth.models.User,
        models.SET_NULL,
        null=True,
        db_index=True)

    item = models.ForeignKey(Product, models.SET_NULL, null=True)

    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'user']

    def save(self, *args, **kwargs):
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def __str__(self):
        name = str(self.item)
        if self.note:
            name += f' ({self.note}) '
        name += f'x{self.quantity}'
        return name
