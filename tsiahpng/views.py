import datetime

from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import gettext as _

from django.contrib import auth
from django.contrib import messages

from . import models
from . import utils

import account.views


def homepage(request):
    opened_orders = models.Order.objects.filter(is_open=True, is_active=True)

    # quick ordering
    today = timezone.localtime().date()
    endday = today + datetime.timedelta(3)
    upcoming_orders = (opened_orders
        .filter(order_date__gte=today,order_date__lte=endday)
        .order_by('-order_date', 'create_time')) # yapf: disable

    # user
    last_user = request.session.get('cart/last_user')

    return render(
        request, 'homepage.html', {
            'last_user': last_user,
            'opened_orders': opened_orders,
            'upcoming_orders': upcoming_orders,
        })


def menu_list(request):
    shops = models.Shop.objects.filter(is_active=True)

    shop_per_page = 25
    if hasattr(settings, 'SHOP_PER_PAGE'):
        shop_per_page = getattr(settings, 'SHOP_PER_PAGE')
    paginator = Paginator(shops, shop_per_page)

    page = utils.try_parse(request.GET.get('p'), 1)
    shops = paginator.get_page(page)

    return render(request, 'menu/list.html', {
        'title': _('Menu List'),
        'shops': shops,
    })


def menu_detail(request, shop_id):
    shop = models.Shop.objects.get(id=shop_id)
    categories = models.Category.objects.filter(
        id__in=shop.products().values_list('category').order_by().distinct())

    # organize the products
    category_dict = []
    for category in categories:
        products = shop.products(category=category)
        if products:
            category_dict.append((category, products))

    unsorted_products = shop.products(category__isnull=True)
    if unsorted_products:
        category_dict.append((_('Unsorted'), unsorted_products))

    return render(request, 'menu/detail.html', {
        'title': shop.name,
        'shop': shop,
        'menu': category_dict,
    })


def menu_add(request, shop_id):
    shop = models.Shop.objects.get(id=shop_id)

    if not shop.allow_user_modify:
        messages.error(request,
                       _('Cannot add product to {shop}').format(shop=shop))
        return redirect('menu_detail', shop_id=shop_id)

    # infos on page
    title = _('Add product to {shop}').format(shop=shop.name)

    # proceed post
    if request.method == 'POST' and utils.is_new_post(request):
        # attributes
        category_id = utils.try_parse(request.POST.get('category'), -1)
        if category_id == -1:
            category = None
        else:
            category = models.Category.objects.get(id=category_id)

        could_save = True

        name = request.POST.get('name')
        if not name:
            messages.error(request, _('Name could not be empty'))
            could_save = False

        price = utils.try_parse(request.POST.get('price'))
        if price <= 0:
            messages.error(request, _('Price should be positive number'))
            could_save = False

        # create
        if could_save:
            obj = models.Product.objects.create(
                shop=shop,
                category=category,
                name=name,
                price=price,
            )

            messages.success(request,
                             _('Successfully add {item}').format(item=obj))
            request.session[f'menu_add/last_category/{shop_id}'] = category_id

    # more infos on page
    categories = models.Category.objects.all()
    last_category = request.session.get(f'menu_add/last_category/{shop_id}',
                                        -1)

    return render(
        request, 'menu/add.html', {
            'title': title,
            'shop': shop,
            'categories': categories,
            'last_category': last_category,
            **utils.get_messages(request),
        })


def order_list(request):
    orders = models.Order.objects.filter(is_active=True)

    order_per_page = 25
    if hasattr(settings, 'ORDER_PER_PAGE'):
        order_per_page = getattr(settings, 'ORDER_PER_PAGE')
    paginator = Paginator(orders, order_per_page)

    page = utils.try_parse(request.GET.get('p'), 1)
    orders = paginator.get_page(page)

    return render(request, 'order/list.html', {
        'title': _('Order List'),
        'orders': orders,
    })


def order_create(request):
    if request.method == 'POST' and utils.is_new_post(request):
        alias = request.POST.get('name')
        shop_id = request.POST['shop']
        shop = models.Shop.objects.get(id=shop_id)
        date = datetime.datetime.strptime(request.POST['date'], '%Y/%m/%d')
        note = request.POST.get('note')

        obj = models.Order.objects.create(
            alias=alias,
            shop=shop,
            order_date=date,
            note=note,
        )

        request.session['order_create/last_shop'] = shop_id

        return redirect('order_detail', order_id=obj.id)

    shops = models.Shop.objects.filter(is_active=True)
    default_date = utils.order_date_default()
    last_shop = request.session.get('order_create/last_shop')

    return render(
        request, 'order/create.html', {
            'title': _('Create Order'),
            'shops': shops,
            'default_date': default_date,
            'last_shop': last_shop,
            **utils.get_messages(request),
        })


def order_detail(request, order_id):
    order = models.Order.objects.get(id=order_id)

    # proceed post
    if request.method == 'POST':
        order_detail_post(request, order)

    # organize tickets, for order summary
    tickets = order.tickets()

    products = tickets.values_list('item').order_by().distinct()
    products = models.Product.objects.filter(id__in=products)

    grouped_tickets = []
    for product in products:
        related_tickets = tickets.filter(item=product)
        if len(related_tickets) == 0:
            continue

        # collate
        collated_tickets = models.Ticket.organize(related_tickets)
        desc = []

        # original taste
        has_original = False
        if collated_tickets[0].note is None:
            has_original = True
            original = collated_tickets[0]
            if len(collated_tickets) == 1:
                desc.append(_('×{qty:,}').format(qty=original.quantity))
            else:
                desc.append(
                    _('Original ×{qty:,}').format(qty=original.quantity))

        # special
        special = collated_tickets
        if has_original:
            special = collated_tickets[1:]

        for ticket in special:
            desc.append(f'{ticket.note} ×{ticket.quantity}')

        grouped_tickets.append((product, ', '.join(desc)))

    # organize tickets (for personal summary)
    users = tickets.values_list('user').order_by().distinct()
    users = auth.models.User.objects.filter(id__in=users)

    person_tickets = []
    for user in users:
        related_tickets = tickets.filter(user=user)
        if len(related_tickets) == 0:
            continue

        collated_tickets = models.Ticket.organize(related_tickets)
        subtotal = related_tickets.aggregate(val=Sum('price'))['val']

        person_tickets.append((
            user,
            ', '.join(str(t) for t in collated_tickets),
            subtotal,
        ))

    # templates
    templates = models.SummaryTemplate.objects.filter(is_active=True)

    # user
    last_user = request.session.get('cart/last_user')

    return render(
        request, 'order/detail.html', {
            'title': str(order),
            'order': order,
            'last_user': last_user,
            'grouped_tickets': grouped_tickets,
            'person_tickets': person_tickets,
            'summary_templates': templates,
            **utils.get_messages(request)
        })


def order_detail_post(request, order) -> (bool, str):
    if not order.is_open:
        messages.error(request, _('Order is closed. Could not add ticket.'))
        return
    if not utils.is_new_post(request):
        return

    user_id = request.POST.get('user')
    if not user_id:
        messages.error(request, _('Please specific a user'))
        return

    user = auth.models.User.objects.get(id=user_id)
    request.session['cart/last_user'] = str(user_id)

    items_ids = set()
    for item_id in request.POST.get('tickets', '').split(','):
        try:
            items_ids.add(int(item_id))
        except (TypeError, ValueError):
            ...
    items = models.Product.objects.filter(id__in=items_ids)

    sum_qty = 0
    sum_price = 0
    tickets = []
    for item in items:
        qty = utils.try_parse(request.POST.get(f'quantity-{item.id}'))
        if qty <= 0:
            continue

        price = utils.try_parse(request.POST.get(f'price-{item.id}'))
        if price < 0:
            continue

        sum_qty += qty
        sum_price += price

        note = request.POST.get(f'note-{item.id}')

        tickets.append(
            models.Ticket.objects.create(
                order=order,
                user=user,
                item=item,
                quantity=qty,
                price=price,
                note=note,
            ))

    if sum_qty == 0:
        messages.error(request, _('No any valid order is received.'))
        return

    else:
        username = user.get_full_name()
        if not username:
            username = user.get_username()

        msg = _('{user} ordered {items}; ${price:,} in total.').format(
            user=username,
            items=', '.join(str(t) for t in tickets),
            price=sum_price,
        )

        messages.success(request, msg)


def order_close(request, order_id):
    order = models.Order.objects.get(id=order_id)

    if not order.is_open:
        return redirect('order_detail', order_id=order_id)

    if request.method == 'POST' and request.POST.get('close', False):
        order.is_open = False
        order.save()

        messages.success(request, _('Successfully closed this order'))

        if request.POST.get('link-account', 'off') == 'on':
            passbook_id = utils.try_parse(request.POST.get('passbook'))
            if account.views.add_post(request, passbook_id):
                request.session['order_close/last_passbook'] = passbook_id

        return redirect('order_detail', order_id=order_id)

    last_passbook = request.session.get('order_close/last_passbook')

    return render(
        request, 'order/close.html', {
            'title': _('Close order'),
            'order': order,
            'last_passbook': last_passbook,
            **utils.get_messages(request),
        })
