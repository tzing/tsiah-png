from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import django.core.validators
import django.contrib.auth.models

from . import utils

#TODO customized user


class Shop(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name=_('Shop name'),
        max_length=256,
        unique=True,
    )

    priority = models.IntegerField(
        verbose_name=_('Priority'),
        default=0,
        db_index=True,
    )

    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)

    image = models.ImageField(
        verbose_name=_('Menu/shop image'),
        null=True,
        blank=True,
        validators=[django.core.validators.validate_image_file_extension])

    note = models.TextField(
        verbose_name=_('Note'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Shop')
        verbose_name_plural = _('Shops')

        ordering = ['-priority']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = None
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def products(self, **kwargs):
        return Product.objects.filter(shop=self, is_active=True, **kwargs)


class Category(models.Model):
    """Categories of the products
    """
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name=_('Category name'),
        max_length=256,
        unique=True,
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Product(models.Model):
    """The products for sale
    """
    id = models.AutoField(primary_key=True)

    shop = models.ForeignKey(
        verbose_name=_('Shop'),
        to=Shop,
        on_delete=models.CASCADE,
        db_index=True,
    )

    category = models.ForeignKey(
        verbose_name=_('Category'),
        to=Category,
        on_delete=models.SET_NULL,
        db_index=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)

    priority = models.IntegerField(
        verbose_name=_('Priority'),
        default=0,
        db_index=True,
    )

    name = models.CharField(
        verbose_name=_('Product name'),
        max_length=256,
    )

    price = models.PositiveIntegerField(verbose_name=_('Price'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

        unique_together = ('shop', 'name')

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

    shop = models.ForeignKey(
        verbose_name=_('Shop'),
        to=Shop,
        on_delete=models.SET_NULL,
        null=True,
    )

    order_date = models.DateField(
        verbose_name=_('Order date'),
        default=utils.order_date_default,
        db_index=True,
    )

    create_time = models.DateTimeField(
        verbose_name=_('Creation time'),
        auto_now_add=True,
    )

    is_open = models.BooleanField(verbose_name=_('Is opened'), default=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)

    alias = models.CharField(
        verbose_name=_('Order alias'),
        max_length=256,
        blank=True,
        null=True,
    )

    note = models.TextField(
        verbose_name=_('Note'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

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

    order = models.ForeignKey(
        verbose_name=_('Order'),
        to=Order,
        on_delete=models.CASCADE,
        db_index=True,
    )

    user = models.ForeignKey(
        verbose_name=_('User'),
        to=django.contrib.auth.models.User,
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )

    item = models.ForeignKey(
        verbose_name=_('Item'),
        to=Product,
        on_delete=models.SET_NULL,
        null=True,
    )

    quantity = models.IntegerField(verbose_name=_('Quantity'), default=0)
    price = models.IntegerField(verbose_name=_('Price'), default=0)

    note = models.TextField(
        verbose_name=_('Note'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Ordered Item')
        verbose_name_plural = _('Ordered Items')

        ordering = ['order', 'user']

    def save(self, *args, **kwargs):
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def __str__(self):
        name = str(self.item)
        if self.note:
            name += f' ({self.note}) '
        name += f'×{self.quantity}'
        return name

    @staticmethod
    def organize(tickets):
        """Organized scattered tickets into distinct itmes.

        Parameters
        ----------
            tickets : query set
                query set of models.Ticket object

        Returns
        -------
            tickets : list of models.Ticket
                a set of distinct tickets; NOTE these tickets are created as
                memory objects and should not save to database, or there might
                exists duplicated projects.
        """
        assert isinstance(tickets, models.query.QuerySet)
        assert tickets.model is Ticket

        all_products_id = tickets.values_list('item').order_by().distinct()
        all_products = Product.objects.filter(id__in=all_products_id)

        organized_tickets = []
        for product in all_products:
            related = tickets.filter(item=product)

            normals = related.filter(note__isnull=True)
            if len(normals) > 0:
                organized_tickets.append(Ticket._aggregate_tickets(normals))

            if len(normals) == len(related):
                continue

            specials = related.filter(note__isnull=False)
            notes = specials.values_list(
                'note', flat=True).order_by().distinct()
            for note in notes:
                same_ticket = specials.filter(note=note)
                organized_tickets.append(
                    Ticket._aggregate_tickets(same_ticket))

        return organized_tickets

    @staticmethod
    def _aggregate_tickets(tickets):
        assert len(tickets) > 0
        sample = tickets.first()
        return Ticket(
            item=sample.item,
            quantity=tickets.aggregate(val=models.Sum('quantity'))['val'],
            price=tickets.aggregate(val=models.Sum('price'))['val'],
            note=sample.note,
        )


class SummaryTemplate(models.Model):
    """This class provide a template to render a pure-text summary for ordering
    the meal via instant message app, since many of the shop we are eating provides
    the order-ahead or delivery service.
    """
    id = models.AutoField(primary_key=True)

    alias = models.CharField(
        verbose_name=_('Template name'),
        max_length=256,
        blank=True,
        null=True,
    )

    # TODO need validation
    template = models.TextField(verbose_name=_('Template'))

    priority = models.IntegerField(
        verbose_name=_('Priority'),
        default=0,
        db_index=True,
    )

    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)

    class Meta:
        verbose_name = _('Template of summary string')
        verbose_name_plural = _('Templates of summary string')

        ordering = ['-priority']

    def __str__(self):
        if self.alias:
            return self.alias
        elif len(self.template) > 20:
            return self.template[:17] + '...'
        else:
            return self.template

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = None
        super().save(*args, **kwargs)

    def render(self, order):
        """Render the string use this template.

        Parameters
        ----------
            order : Order
                the order to render

        Returns
        -------
            summary_string : str
                a summary to the order
        """
        assert isinstance(order, Order)
        from django.template import Template, Context

        template = '{% load ticket_stringify %}' + self.template
        summary_string = Template(template).render(
            Context({
                'order': order,
                'tickets': Ticket.organize(order.tickets()),
            }))

        return summary_string
