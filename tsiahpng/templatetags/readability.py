"""Template tags for improving code readability
"""
import django.template
from django.utils.translation import gettext as _

register = django.template.Library()


@register.filter
def to_username(user):
    """Converting user object to username
    """
    name = user.get_full_name()
    if not name.strip():
        name = user.get_username()
    return name


@register.filter
def shop_summary(shop):
    """Generate short summary string of the shop.
    """
    num_products = len(shop.products())
    num_categories = len(
        shop.products().values_list('category').order_by().distinct())

    return _(
        '{num_cat:,} categories. {num_product:,} documented products.').format(
            num_cat=num_categories,
            num_product=num_products,
        )
