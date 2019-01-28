"""Template tags for providing short summary to the object.
"""
import django.template
from django.db.models import Sum
from django.utils.translation import gettext as _

import tsiahpng.models as models

register = django.template.Library()


@register.filter
def shop_summary(shop):
    """Generate shop summary string.
    """
    assert isinstance(shop, models.Shop)

    num_products = len(shop.products())
    num_categories = len(
        shop.products().values_list('category').order_by().distinct())

    return _(
        '{num_cat:,} categories. {num_product:,} documented products.').format(
            num_cat=num_categories,
            num_product=num_products,
        )


@register.filter
def per_category_quantity(order):
    """Given per-category ordered quantity of the order.
    """
    assert isinstance(order, models.Order)

    tickets = order.tickets()
    items = tickets.values_list('item').order_by().distinct()
    items = models.Product.objects.filter(id__in=items)

    categories = items.values_list('category').order_by().distinct()
    categories = models.Category.objects.filter(id__in=categories)

    # per category quantity
    counting = []
    for category in categories:
        related_items = items.filter(category=category)
        related_tickets = tickets.filter(item__in=related_items)

        count = related_tickets.aggregate(val=Sum('quantity'))['val']
        if isinstance(count, int):
            counting.append(
                _('{count} {category}').format(count=count, category=category))

    # per category quantity - no category
    related_items = items.filter(category__isnull=True)
    related_tickets = tickets.filter(item__in=related_items)
    count = related_tickets.aggregate(val=Sum('quantity'))['val']
    if isinstance(count, int):
        counting.append(_('{count} others').format(count=count))

    # build string
    return _(', ').join(counting)
