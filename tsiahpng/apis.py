from django.http import HttpResponse, JsonResponse

import django.db.models
import django.contrib.auth.models

from . import models
from . import utils


def query_order(request, order_id):
    """Get detailed info to specific order

    Query Parameters
    ----------------
    """
    # parse requests
    return_totals = utils.str2bool(request.GET.get('total'))
    return_subtotals = utils.str2bool(request.GET.get('subtotal'))

    # get values
    order = models.Order.objects.get(id=order_id)
    related_users = django.contrib.auth.models.User.objects.filter(
        id__in=order.tickets().values_list('user').order_by().distinct())

    if return_subtotals:
        tickets = order.tickets()

        subtotals = []
        for user in related_users:
            user_tickets = tickets.filter(user=user)
            balance = user_tickets.aggregate(
                val=django.db.models.Sum('price'))['val']
            subtotals.append((user, balance))

    # returning info
    context = {}

    if return_totals:
        context['total'] = order.total_price()

    if return_subtotals:
        field = {}
        context['subtotal'] = field
        for user, balance in subtotals:
            field[user.id] = balance

    return JsonResponse(context)


def summary_order(request, order_id):
    """Generate a summary text to the order

    Query Parameters
    ----------------
        template (default: first template in db)
            id to the template
    """
    order = models.Order.objects.get(id=order_id)

    template_id = request.GET.get('template')
    if template_id is None:
        template = models.SummaryTemplate.objects.first()
    else:
        template = models.SummaryTemplate.objects.get(id=template_id)

    return HttpResponse(template.render(order))
