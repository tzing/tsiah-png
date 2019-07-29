"""Template tags for formatting the tickets
"""
import django.template

from django.utils.translation import gettext_lazy as _


from .. import models
from .. import utils

register = django.template.Library()


@register.filter
def no_qty(ticket):
    """Render ticket without quantity if the quantity is one.
    """
    assert isinstance(ticket, (models.Ticket, utils.DisplayTicket))
    if ticket.quantity > 1:
        return str(ticket)
    elif ticket.note:
        return _("{item}({note})").format(item=ticket.item, note=ticket.note)
    else:
        return str(ticket.item)


@register.filter()
def organize_tickets(tickets):
    return utils.organize_tickets(tickets)
