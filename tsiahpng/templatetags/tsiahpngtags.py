from collections import OrderedDict
from datetime import date, datetime
import re

import django.template
import django.contrib.auth.models as auth

from django.db.models import Sum
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .. import models
from .. import settings
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

    return django.template.defaultfilters.date(value, "Y/n/j")


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
            counts.append(_("{item} ×{qty}").format(item=cat, qty=sum_qty))

    unsorted_products = products.filter(category=None)
    if unsorted_products:
        sum_qty = order.tickets(item__in=unsorted_products).aggregate(
            val=Sum("quantity")
        )["val"]
        counts.append(_("{item} ×{qty}").format(item=_("Unsorted"), qty=sum_qty))

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


@register.filter()
def organize_tickets(tickets):
    return utils.organize_tickets(tickets)


@register.simple_tag()
def site_settings(name):
    assert isinstance(name, str)
    assert name.upper() in ("USE_TWEMOJI",)
    return getattr(settings, name.upper())


@register.filter()
def group_by_users(items):
    assert isinstance(items, models.models.QuerySet)

    user_ids = items.values_list("user").order_by().distinct()
    related_users = auth.User.objects.filter(id__in=user_ids)

    # items from active users
    grouped_items = OrderedDict()
    for user in related_users.filter(is_active=True):
        related_items = items.filter(user=user)
        grouped_items[user] = related_items

    # items from inactive users
    inactive_users = related_users.filter(is_active=False)
    if inactive_users:
        related_items = items.filter(user__in=inactive_users)
        grouped_items[None] = related_items

    return grouped_items


@register.filter()
def remove_link(text):
    pattern = re.compile(r"<\s*\/?\s*a\b[^>]*?>")
    return mark_safe(pattern.sub("", text))
