from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from django.contrib import auth
from django.contrib import messages

import tsiahpng.models
import tsiahpng.utils

from . import models


def overview(request):
    return render(request, 'account/list.html', {
        'title': _('Accounting'),
        'passbooks': models.Passbook.objects.all(),
    })


def detail(request, passbook_id):
    passbook = models.Passbook.objects.get(id=passbook_id)
    user_balances = passbook.peruser_balance()
    users, balances = zip(*user_balances)

    # infos for each event
    transaction_table = []
    for event in passbook.events():
        balance = []
        transactions = event.transactions()
        for user in users:
            transaction = transactions.filter(user=user)
            if len(transaction) == 0:
                balance.append(None)
            else:
                balance.append(transaction.get().balance)

        transaction_table.append((event, balance))

    # collect messages
    storage = messages.get_messages(request)
    success_message = list(
        filter(lambda m: m.level == messages.SUCCESS, storage))

    return render(
        request, 'account/detail.html', {
            'title': passbook,
            'passbook': passbook,
            'user_balances': user_balances,
            'active_users': users,
            'balances': balances,
            'transaction_table': transaction_table,
            'success_message': success_message,
        })


def add(request, passbook_id):
    """Create a new event and add transactions into the passbook
    """
    passbook = models.Passbook.objects.get(id=passbook_id)

    # post
    if request.method == 'POST' and add_post(request, passbook_id):
        return redirect('account:detail', passbook_id=passbook_id)

    # collect messages
    storage = messages.get_messages(request)
    error_message = list(filter(lambda m: m.level == messages.ERROR, storage))

    return render(
        request, 'account/add.html', {
            'title': _('Add transaction'),
            'passbook': passbook,
            'error_message': error_message,
        })


def add_post(request, passbook_id):
    """Proceed post action for creating event and transactions

    Return
    ------
        is_created : bool
            if the event is created
    """
    assert request.method == 'POST'

    # read fields
    passbook = models.Passbook.objects.get(id=passbook_id)

    title = request.POST.get('title')

    order = request.POST.get('order')
    if order:
        order = tsiahpng.models.Order.objects.get(id=int(order))

    event = models.Event.objects.create(
        book=passbook, title=title, related_order=order)

    users = request.POST.get('user', '')

    # create transactions
    transaction_created = False
    for user_id in users.split(','):
        user_id = tsiahpng.utils.try_parse(user_id, -1)
        if user_id == -1:
            continue

        user = auth.models.User.objects.get(id=user_id)
        balance = tsiahpng.utils.try_parse(
            request.POST.get(f'balance-{user_id}'))
        if balance == 0:
            continue

        models.Transaction.objects.create(
            event=event, user=user, balance=balance)
        transaction_created = True

    if transaction_created:
        msg = _('Successfully added transaction: {event}').format(event=event)
        messages.add_message(request, messages.SUCCESS, msg)
        return True

    else:
        event.delete()
        msg = _('At least one change should be specified for creating '
                'a transaction')
        messages.add_message(request, messages.ERROR, msg)
        return False
