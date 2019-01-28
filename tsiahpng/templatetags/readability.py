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
