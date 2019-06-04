from django.db import models
from django.utils.translation import gettext_lazy as _

from . import default
from . import settings


class Shop(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(verbose_name=_("Shop name"), max_length=256, unique=True)

    ordering = models.IntegerField(
        verbose_name=_("Ordering"), default=-1, db_index=True
    )

    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Unselect this instead of deleting shop."),
    )

    changeable = models.BooleanField(
        verbose_name=_("Changeable"),
        default=True,
        help_text=_("Uncheckeded if users are not allowed to change menu."),
    )

    image = models.ImageField(
        verbose_name=_("Image"),
        null=True,
        blank=True,
        help_text=_("Menu or shop photo."),
    )

    note = models.TextField(verbose_name=_("Note"), null=True, blank=True)

    class Meta:
        verbose_name = _("Shop")
        verbose_name_plural = _("Shops")

        ordering = ["-ordering"]

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

    def related_categories(self):
        category_ids = self.products().values_list("category").order_by().distinct()
        categories = Category.objects.filter(id__in=category_ids)
        return categories


class Category(models.Model):
    """Product Categories.
    """

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name=_("Category name"), max_length=256, unique=True
    )

    ordering = models.IntegerField(
        verbose_name=_("Ordering"), default=-1, db_index=True
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

        ordering = ["-ordering"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """The products for sale.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name=_("Product name"), max_length=256)

    shop = models.ForeignKey(
        verbose_name=_("Shop"), to="Shop", on_delete=models.CASCADE, db_index=True
    )
    category = models.ForeignKey(
        verbose_name=_("Category"),
        to="Category",
        on_delete=models.SET_NULL,
        db_index=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Unselect this instead of deleting product."),
    )
    changeable = models.BooleanField(
        verbose_name=_("Changeable"),
        default=True,
        help_text=_("Unchecked if users are not allowed to make changes."),
    )
    mergable = models.BooleanField(
        verbose_name=_("Mergable"),
        default=True,
        help_text=_("Unchecked if its quantity should not be summarized."),
    )

    ordering = models.IntegerField(
        verbose_name=_("Ordering"), default=-1, db_index=True
    )

    price = models.PositiveIntegerField(
        verbose_name=_("Price"), default=settings.DEFAULT_PROD_PRICE
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

        unique_together = ("shop", "name")

        ordering = ["category", "-ordering"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.category:
            self.category = None
        super().save(*args, **kwargs)


class Order(models.Model):
    """The exact order that would be sent to shop owner; The containe to
    collect the tickets from each user.
    """

    id = models.AutoField(primary_key=True)
    alias = models.CharField(
        verbose_name=_("Order alias"), max_length=256, blank=True, null=True
    )
    shop = models.ForeignKey(
        verbose_name=_("Shop"), to=Shop, on_delete=models.SET_NULL, null=True
    )
    order_date = models.DateField(
        verbose_name=_("Order date"), default=default.default_order_date, db_index=True
    )

    is_available = models.BooleanField(
        verbose_name=_("Available"),
        default=True,
        help_text=_("Unselect this to prevent users from ordering."),
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Unselect this instead of deleting order."),
    )

    note = models.TextField(verbose_name=_("Note"), null=True, blank=True)

    date_created = models.DateTimeField(
        verbose_name=_("Date created"), auto_now_add=True
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

        ordering = ["-order_date", "-date_created"]

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
            return _("Ordering {shop} on {time:%Y/%m/%d}").format(
                shop=self.shop, time=self.order_date
            )

    def tickets(self, **kwargs):
        return Ticket.objects.filter(order=self, **kwargs)

    def sum_quantity(self):
        sum_qty = self.tickets().aggregate(val=models.Sum("quantity"))["val"]
        if not sum_qty:
            return 0
        return sum_qty

    def sum_cost(self):
        sum_cost_ = self.tickets().aggregate(val=models.Sum("cost"))["val"]
        if not sum_cost_:
            return 0
        return sum_cost_

    sum_quantity.short_description = _("Total ordered quantity")
    sum_cost.short_description = _("Total cost")


class Ticket(models.Model):
    """A ticket represents one item ordered by one user.
    """

    id = models.AutoField(primary_key=True)

    order = models.ForeignKey(
        verbose_name=_("Order"), to=Order, on_delete=models.CASCADE, db_index=True
    )

    user = models.ForeignKey(
        verbose_name=_("User"),
        to="auth.User",
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )

    item = models.ForeignKey(
        verbose_name=_("Ordered Product"),
        to=Product,
        on_delete=models.SET_NULL,
        null=True,
    )

    quantity = models.IntegerField(verbose_name=_("Quantity"), default=0)
    cost = models.IntegerField(verbose_name=_("Cost"), default=0)

    note = models.CharField(
        verbose_name=_("Note"), max_length=1024, null=True, blank=True
    )

    class Meta:
        verbose_name = _("Ordered Item")
        verbose_name_plural = _("Ordered Items")

    def save(self, *args, **kwargs):
        if not self.note:
            self.note = None
        super().save(*args, **kwargs)

    def __str__(self):
        name = f"{self.item} ×{self.quantity}"
        if self.note:
            return f"{name} ({self.note})"
        else:
            return name


class WelcomeText(models.Model):
    """Welcome string to be displayed in homepage.
    """

    id = models.AutoField(primary_key=True)

    title = models.CharField(verbose_name=_("Title"), max_length=128)
    subtitle = models.CharField(
        verbose_name=_("Subtitle"), max_length=256, null=True, blank=True
    )

    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Unselect this to disable this text."),
    )

    class Meta:
        verbose_name = _("Welcome Text")
        verbose_name_plural = _("Welcome Texts")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.subtitle:
            self.subtitle = None
        super().save(*args, **kwargs)
