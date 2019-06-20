import collections

from django.db.models import Sum
from django.template import Library
from django.contrib import auth

from .. import models

register = Library()


@register.filter()
def per_user_balance(passbook, only_active=True):
    events = passbook.events()
    transactions = models.Transaction.objects.filter(event__in=events)

    user_ids = transactions.values_list("user").order_by().distinct()
    users = auth.models.User.objects.filter(id__in=user_ids, is_active=True)

    balances = collections.OrderedDict()
    for user in users.order_by():
        related_transactions = transactions.filter(user=user)
        balance = related_transactions.aggregate(val=Sum("balance"))["val"]
        balances[user] = balance or 0

    if not only_active:
        inactive_users = auth.models.User.objects.filter(
            id__in=user_ids, is_active=False
        )
        if not inactive_users:
            return balances

        related_transactions = transactions.filter(user__in=inactive_users)
        if not related_transactions:
            return balances

        balance = related_transactions.aggregate(val=Sum("balance"))["val"]
        balances[None] = balance or 0

    return balances


@register.filter()
def per_user_balance_include_inactive(passbook):
    """Shortcut, since with statement does not support filter args.
    """
    return per_user_balance(passbook, False)


@register.filter()
def get_user_balance(transactions, users):
    if users[-1] is None:
        active_users = users[:-1]
        has_inactive_users = True
    else:
        active_users = users
        has_inactive_users = False

    # active users
    balances = []
    for user in active_users:
        try:
            balances.append(transactions.get(user=user).balance)
        except models.Transaction.DoesNotExist:
            balances.append(None)

    # inactive users
    if has_inactive_users:
        balance = transactions.exclude(user__in=active_users).aggregate(
            val=Sum("balance")
        )["val"]
        balances.append(balance)

    return balances
