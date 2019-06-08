from datetime import date, datetime

import django.template

from django.db.models import Sum
from django.utils.translation import gettext as _

from .. import models
from .. import utils

register = django.template.Library()


@register.filter(expects_localtime=True)
def short_naturalday(value):
    """An patched version to ``django.contrib.humanize``
    """
    tzinfo = getattr(value, "tzinfo", None)
    try:
        value = date(value.year, value.month, value.day)
    except AttributeError:
        # Passed value wasn't a date object
        return value
    today = datetime.now(tzinfo).date()
    delta = value - today
    if delta.days == 0:
        return _("today")
    elif delta.days == 1:
        return _("tomorrow")
    elif delta.days == -1:
        return _("yesterday")

    # patched feature: hide year if the date is current year
    if today.year == value.year:
        return django.template.defaultfilters.date(value, "n/j")

    return django.template.defaultfilters.date(value, "%Y/%n/%j")


@register.filter()
def percategory_quantity(order):
    assert isinstance(order, models.Order)
    # get products
    product_ids = order.tickets().values_list("item").order_by().distinct()
    if not product_ids:
        return _("no items")

    products = models.Product.objects.filter(id__in=product_ids)

    # get categories
    category_ids = products.values_list("category").order_by().distinct()
    categories = models.Category.objects.filter(id__in=category_ids)

    # counting
    counts = []
    for cat in categories:
        related_products = products.filter(category=cat)
        sum_qty = order.tickets(item__in=related_products).aggregate(
            val=Sum("quantity")
        )["val"]
        if sum_qty:
            counts.append(_("{cat} ×{qty}").format(cat=cat, qty=sum_qty))

    unsorted_products = products.filter(category=None)
    if unsorted_products:
        sum_qty = order.tickets(item__in=unsorted_products).aggregate(
            val=Sum("quantity")
        )["val"]
        counts.append(_("{cat} ×{qty}").format(cat=_("Unsorted"), qty=sum_qty))

    # join string
    return _(", ").join(counts)


@register.filter()
def username(user):
    return utils.get_username(user)


@register.filter()
def dictsum(value, arg):
    try:
        return sum(getattr(v, arg) for v in value)
    except AttributeError:
        return 0
