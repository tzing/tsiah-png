import json

from django.core.paginator import Paginator
from django.contrib import auth
from django.contrib import messages
from django.db.models import Window, Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from tsiahpng import utils
import tsiahpng.models

from . import forms
from . import models
from . import settings


def account_list(request):
    passbooks = models.Passbook.objects.filter(is_active=True)

    idx_page = utils.try_parse(request.GET.get("p"), 1)
    paginator = Paginator(passbooks, settings.PASSBOOK_PER_PAGE)

    return render(
        request,
        "tsiahpng/account/index.pug",
        {
            "title": _("Account"),
            "passbooks": paginator.get_page(idx_page),
            "messages": messages.get_messages(request),
            "transaction_creatable": settings.ALLOW_ANYONE_ALTER_TRANSACTION,
        },
    )


def account_detail(request, passbook_id):
    # get passbook
    try:
        passbook = models.Passbook.objects.get(id=passbook_id, is_active=True)
    except models.Passbook.DoesNotExist:
        messages.error(request, _("Passbook #{id} not exists.").format(id=passbook_id))
        return redirect("tsiahpng-account:list")

    # get related users
    user_ids = (
        models.Transaction.objects.filter(event__in=passbook.events())
        .values_list("user")
        .distinct()
    )
    related_users = auth.models.User.objects.filter(id__in=user_ids)
    active_users = tuple(related_users.filter(is_active=True))
    inactive_users = tuple(related_users.filter(is_active=False))

    if inactive_users:
        users = (*active_users, None)
    else:
        users = active_users

    # get balances
    # https://stackoverflow.com/a/49569644/6107902
    events = passbook.events().annotate(
        balance=Window(Sum("subtotal"), order_by=F("id").asc())
    )

    # build table
    idx_page = utils.try_parse(request.GET.get("p"), 1)
    paginator = Paginator(events, settings.TRANSACTION_PER_PAGE)

    return render(
        request,
        "tsiahpng/account/detail.pug",
        {
            "title": str(passbook),
            "passbook": passbook,
            "messages": messages.get_messages(request),
            "users": users,
            "events": paginator.get_page(idx_page),
            "transaction_creatable": passbook.changeable
            and settings.ALLOW_ANYONE_ALTER_TRANSACTION,
        },
    )


def create_event(request, passbook_id):
    # get passbook
    try:
        passbook = models.Passbook.objects.get(id=passbook_id, is_active=True)
    except models.Passbook.DoesNotExist:
        messages.error(request, _("Passbook #{id} not exists.").format(id=passbook_id))
        return redirect("tsiahpng-account:list")

    # permission check #2
    if not passbook.changeable or not settings.ALLOW_ANYONE_ALTER_TRANSACTION:
        messages.error(request, _("No enough permission for this operation."))
        return redirect("tsiahpng-account:detail", passbook_id)

    # handle post
    if request.method == "POST" and utils.is_new_post(request):
        form = forms.AddEventForm(request.POST)
        event = form.to_model()
        if event:
            messages.success(
                request, _('Successfully add record "{event}".').format(event=event)
            )
            return redirect("tsiahpng-account:detail", passbook_id=passbook_id)
        else:
            messages.error(request, _("Invalid requests."))

    # get related users
    events = passbook.events()
    transactions = models.Transaction.objects.filter(event__in=events)

    user_ids = transactions.values_list("user").distinct()
    related_users = auth.models.User.objects.filter(id__in=user_ids, is_active=True)
    related_user_ids = [user.id for user in related_users]

    return render(
        request,
        "tsiahpng/account/create_event.pug",
        {
            "title": _("Add record on {passbook}").format(passbook=passbook),
            "passbook": passbook,
            "messages": messages.get_messages(request),
            "users": auth.models.User.objects.filter(is_active=True),
            "related_users": json.dumps(related_user_ids),
        },
    )


def account_list_api(request):
    passbooks = models.Passbook.objects.filter(is_active=True)

    return JsonResponse(
        {
            "success": True,
            "results": [{"name": str(book), "value": book.id} for book in passbooks],
        }
    )


def order_close(request, order_id):
    if not request.method == "POST" or not utils.is_new_post(request):
        return redirect("tsiahpng:order_detail", order_id)

    # get order
    try:
        order = tsiahpng.models.Order.objects.get(id=order_id, is_active=True)
    except tsiahpng.models.Order.DoesNotExist:
        messages.error(request, _("Order #{id} id not exists.").format(id=order_id))
        return redirect("tsiahpng:order_list")

    # operate
    order.is_available = False
    order.save()

    messages.info(request, _("Order closed."))

    # billing
    if request.POST.get("on_bill") == "on":
        form = forms.AddEventForm(request.POST)
        event = form.to_model()
        if event:
            messages.success(
                request, _('Successfully add record "{event}".').format(event=event)
            )
        else:
            messages.error(request, _("Failed to billing."))

    return redirect("tsiahpng:order_detail", order_id)
