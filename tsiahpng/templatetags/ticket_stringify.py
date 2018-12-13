"""Template tags for formatting the tickets
"""
import django.template

from tsiahpng import models

register = django.template.Library()


@register.filter
def format_ticket(ticket,
                  format_normal='{name}',
                  format_special='{name}({note})',
                  format_count='{desc} ×{quantity}',
                  count_one=True):
    """Format the tickets with the given format.

    For `format_normal` and `format_special`, one could use the tag `{name}`,
    `{price}` and `{note}` for corresponding content. The generated string
    would be passed to be the `{desc}` in the `format_count`, with tag
    `{quantity}` to makeup the final output.

    Option `count_one` provides a variant that do NOT pass the output string
    to quantity formatter when there is only one item ordered. This feature is
    used to shorten the generated message length.

    Parameters
    ----------
        ticket : models.Ticket
            the ticket object
        format_normal : str
            the format to generate the string when the ticket is without note.
        format_special : str
            the format to generate the string when the ticket is WITH note.
        format_count : str
            the format to generate the string of item name and quantity.
        count_one : bool
            whether show the quantity if only one item is taken.

    Returns
    -------
        ticket_summary : str
            the overview of the given ticket
    """
    assert isinstance(ticket, models.Ticket)

    formatter = format_normal
    if ticket.note:
        formatter = format_special

    output = formatter.format(
        name=ticket.item,
        price=ticket.price,
        note=ticket.note,
    )

    if count_one or ticket.quantity > 1:
        output = format_count.format(desc=output, quantity=ticket.quantity)

    return output


@register.filter
def no_qty(ticket):
    """Shortcut to `format_ticket(..., count_one=False)`.
    """
    return format_ticket(ticket, count_one=False)
