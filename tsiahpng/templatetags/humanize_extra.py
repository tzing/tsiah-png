from datetime import date, datetime

import django.template

from django.utils.translation import gettext as _

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
