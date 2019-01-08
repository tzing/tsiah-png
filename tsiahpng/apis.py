from django.http import HttpResponse

from . import models
from . import utils


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
