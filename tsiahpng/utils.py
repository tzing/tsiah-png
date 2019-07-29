import hashlib

from django.db.models import QuerySet, Sum
from django.utils.translation import gettext as _
from django.contrib import auth

from . import models

__all__ = (
    "try_parse",
    "str2bool",
    "get_username",
    "is_new_post",
    "organize_tickets",
    "DisplayTicket",
)


def try_parse(value, default=0, type=int):
    """Try to parse the input value into certian type. Return default on error.
    """
    try:
        return type(value)
    except (TypeError, ValueError):
        return default


def str2bool(txt):
    """Convert string to bool, use for query parameter
    """
    if not bool(txt):
        return False
    return str(txt).lower() in ("1", "y", "yes", "t", "true")


def get_username(user):
    name = user.get_full_name().strip()
    if not name:
        name = user.get_username().strip()
    return name


def get_stuff_ordering(request):
    """Query stuffs for ordering form.
    """
    return {
        "users": auth.models.User.objects.filter(is_active=True),
        "last_user": request.session.get("ordering/last_user"),
    }


def is_new_post(request):
    """A utility to test if the post is duplicated sent, or really the new one.

    Return
    ------
    is_valid : bool
        True if this request is valid.
    """
    post_content = request.POST.urlencode().encode("utf-8")
    hash_str = hashlib.sha1(post_content).hexdigest()
    if request.session.get(f"{request.path}/last_post") == hash_str:
        return False
    request.session[f"{request.path}/last_post"] = hash_str
    return True


def organize_tickets(tickets):
    """Organize scattered tickets into distinct items.

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
    if isinstance(tickets, QuerySet):
        return organize_tickets_qs(tickets)

    product_ids = set(t.item.id for t in tickets)
    products = models.Product.objects.filter(id__in=product_ids)

    organized_tickets = []
    for product in products:
        related_tickets = tuple(filter(lambda t: t.item == product, tickets))

        # original taste
        original_taste = tuple(filter(lambda t: t.note is None, related_tickets))
        if original_taste:
            organized_tickets.append(aggregate_tickets(original_taste))

        if len(original_taste) == len(related_tickets):
            continue

        # those with notes
        special_tastes = tuple(filter(lambda t: t.note is not None, related_tickets))
        notes = set(t.note for t in special_tastes)
        for note in notes:
            same_taste = tuple(filter(lambda t: t.note == note, special_tastes))
            organized_tickets.append(aggregate_tickets(same_taste))

    return organized_tickets


def organize_tickets_qs(tickets):
    assert isinstance(tickets, QuerySet)
    assert tickets.model is models.Ticket

    product_ids = tickets.values_list("item").order_by().distinct()
    products = models.Product.objects.filter(id__in=product_ids)

    organized_tickets = []
    for product in products:
        related_tickets = tickets.filter(item=product)

        # original taste
        original_taste = related_tickets.filter(note__isnull=True)
        if original_taste:
            organized_tickets.append(aggregate_tickets(original_taste))

        if len(original_taste) == len(related_tickets):
            continue

        # those with notes
        special_tastes = related_tickets.filter(note__isnull=False)
        notes = special_tastes.values_list("note", flat=True).order_by().distinct()
        for note in notes:
            same_taste = special_tastes.filter(note=note)
            organized_tickets.append(aggregate_tickets(same_taste))

    return organized_tickets


class DisplayTicket:
    def __init__(self, item, quantity, cost, note):
        self.item = item
        self.quantity = quantity
        self.cost = cost
        self.note = note

    def __str__(self):
        if self.note:
            return _("{item}({note}) ×{qty}").format(
                item=self.item, qty=self.quantity, note=self.note
            )
        else:
            return _("{item} ×{qty}").format(item=self.item, qty=self.quantity)


def aggregate_tickets(tickets):
    assert tickets
    sample = next(iter(tickets))

    item = sample.item
    note = sample.note
    quantity = aggregate_fields(tickets, "quantity")
    cost = aggregate_fields(tickets, "cost")

    if not sample.item.mergable:
        quantity = _("{total} ({separate})").format(
            total=quantity, separate=_("+").join(str(t.quantity) for t in tickets)
        )

    return DisplayTicket(item=item, quantity=quantity, cost=cost, note=note)


def aggregate_fields(tickets, field):
    if isinstance(tickets, QuerySet):
        return tickets.aggregate(val=Sum(field))["val"]
    else:
        return sum(getattr(t, field) for t in tickets)
