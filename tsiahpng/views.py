import datetime

from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import gettext as _
import django.contrib.auth.models as auth_models

from . import models
from . import utils


def homepage(request):
    orders = models.Order.objects.filter(can_order=True)
    users = []
    products = []

    # nearest order
    now = timezone.localtime().date()
    nearest_order = orders.filter(order_date__gte=now).order_by(
        'order_date', 'create_time').first()

    if nearest_order:
        users = auth_models.User.objects.filter(is_active=True)
        products = models.Product.objects.filter(shop=nearest_order.shop)

    return render(
        request, 'homepage.html', {
            'order': nearest_order,
            'users': users,
            'products': products,
            'all_orders': orders,
        })


def menu_list(request):
    shops = models.Shop.objects.all()

    shop_dict = []
    for shop in shops:
        shop_dict.append(
            (shop,
             _('%(num_cat)d categories. %(num_product)d documented products.')
             % {
                 'num_cat': len(models.Category.objects.filter(shop=shop)),
                 'num_product': len(models.Product.objects.filter(shop=shop)),
             }))

    return render(request, 'menu/list.html', {
        'title': _('Menu List'),
        'shops': shop_dict,
    })


def menu_detail(request, shop_id):
    shop = models.Shop.objects.get(id=shop_id)
    categories = models.Category.objects.filter(shop=shop)
    products = models.Product.objects.filter(shop=shop)

    # organize the products
    category_dict = []
    for category in categories:
        category_dict.append((category, products.filter(category=category)))

    unsorted_products = products.filter(category__isnull=True)
    if unsorted_products:
        category_dict.append((_('Unsorted'), unsorted_products))

    # get summary
    summary_products = _(
        'There are %(num_cat)d categories and %(num_product)d products documented:'
    ) % {
        'num_cat': len(categories),
        'num_product': len(products),
    }

    return render(
        request, 'menu/detail.html', {
            'title': shop.name,
            'shop': shop,
            'summary_products': summary_products,
            'categories': category_dict,
        })


def menu_add(request, shop_id):
    shop = models.Shop.objects.get(id=shop_id)

    # infos on page
    title = _('Add product to %(shop)s') % {'shop': shop.name}

    success_message = None
    error_message = []

    # proceed post
    if request.method == 'POST':
        # attributes
        category_id = utils.try_get(request, 'category', default=-1)
        if category_id == -1:
            category = None
        else:
            category = models.Category.objects.get(id=category_id)

        could_save = True

        name = request.POST.get('name', None)
        if not name:
            error_message.append(_('Name could not be empty'))
            could_save = False

        price = utils.try_get(request, 'price')
        if price <= 0:
            error_message.append(_('Price should be positive number'))
            could_save = False

        # create
        if could_save:
            obj = models.Product.objects.create(
                shop=shop,
                category=category,
                name=name,
                price=price,
            )

            success_message = _('Successfully add %(obj)s') % {'obj': obj}

            request.session[f'menu_add/last_category/{shop_id}'] = category_id

    # more infos on page
    categories = models.Category.objects.filter(shop=shop)
    last_category = request.session.get(f'menu_add/last_category/{shop_id}',
                                        -1)

    # page render
    is_compact = request.GET.get('compact', False)
    template = 'menu/add.html'
    if is_compact:
        template = 'menu/add_compact.html'

    return render(
        request, template, {
            'title': title,
            'shop': shop,
            'categories': categories,
            'last_category': last_category,
            'success_message': success_message,
            'error_message': error_message,
        })


def order_list(request):
    orders = models.Order.objects.all()

    return render(request, 'order/list.html', {
        'title': _('Order List'),
        'orders': orders,
    })


def order_create(request):
    if request.method == 'POST':
        alias = request.POST.get('name')
        shop = models.Shop.objects.get(id=request.POST['shop'])
        date = datetime.datetime.strptime(request.POST['date'], '%Y/%m/%d')
        note = request.POST.get('note')

        obj = models.Order.objects.create(
            alias=alias,
            shop=shop,
            order_date=date,
            note=note,
        )

        return redirect('order_list')

    # shops
    shops = models.Shop.objects.all()

    # default date
    day_end = 24
    if hasattr(settings, 'TSIAHPNG_DAY_END'):
        day_end = getattr(settings, 'TSIAHPNG_DAY_END')

    default_date = datetime.datetime.now()
    if default_date.hour >= day_end:
        default_date += datetime.timedelta(days=1)

    return render(request, 'order/create.html', {
        'title': _('Create Order'),
        'shops': shops,
        'default_date': default_date,
    })


def order_detail(request, order_id):
    order = models.Order.objects.get(id=order_id)

    # placeholder
    success_message = None
    error_message = None

    # proceed post
    if request.method == 'POST':
        is_success, message = order_detail_post(request, order)
        if is_success:
            success_message = message
        else:
            error_message = message

    # basic infos for rendering
    users = auth_models.User.objects.filter(is_active=True)
    products = models.Product.objects.filter(shop=order.shop)
    tickets = models.Ticket.objects.filter(order=order)

    # organize tickets (for order summary)
    grouped_tickets = []
    for product in products:
        related_tickets = tickets.filter(item=product)
        if len(related_tickets) == 0:
            continue

        noted_tickets = related_tickets.filter(note__isnull=False)
        if len(noted_tickets) == 0:
            sum_qty = related_tickets.aggregate(val=Sum('quantity'))['val']
            grouped_tickets.append((product, f'x{sum_qty}'))
            continue

        desc = []
        qty_normal = related_tickets.filter(note__isnull=True).aggregate(
            val=Sum('quantity'))['val']
        if qty_normal:
            desc.append(_('Normal x%(qty)d') % {'qty': qty_normal})

        for ticket in noted_tickets:
            desc.append(f'{ticket.note} x{ticket.quantity}')

        grouped_tickets.append((product, ', '.join(desc)))

    total_price = tickets.aggregate(val=Sum('price'))['val']

    # organize tickets (for personal summary)
    person_tickets = []
    for user in users:
        related_tickets = tickets.filter(user=user)
        if len(related_tickets) == 0:
            continue

        username = user.get_full_name()
        if not username:
            username = user.get_username()

        subtotal = related_tickets.aggregate(val=Sum('price'))['val']

        person_tickets.append((
            username,
            ', '.join(str(t) for t in related_tickets),
            subtotal,
        ))

    return render(
        request, 'order/detail.html', {
            'title': str(order),
            'order': order,
            'users': users,
            'products': products,
            'success_message': success_message,
            'error_message': error_message,
            'grouped_tickets': grouped_tickets,
            'total_price': total_price,
            'person_tickets': person_tickets,
        })


def order_detail_post(request, order) -> (bool, str):
    username = request.POST.get('user')
    if not username:
        return False, _('Please specific a user')

    user = auth_models.User.objects.get(username=username)

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
        qty = utils.try_get(request, f'quantity-{item.id}')
        if qty <= 0:
            continue
        sum_qty += qty

        price = utils.try_get(request, f'price-{item.id}')
        if price < 0:
            continue
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
        return False, _('At least one item should be selected')
    else:
        username = user.get_full_name()
        if not username:
            username = user.get_username()
        return True, _('%(user)s ordered %(items)s; $%(price)s in total.') % {
            'user': username,
            'items': ', '.join(str(t) for t in tickets),
            'price': '{:,}'.format(sum_price),
        }


def order_close(request, order_id):
    order = models.Order.objects.get(id=order_id)

    if request.method == 'POST' and request.POST.get('close', False):
        order.can_order = False
        order.save()
        return redirect('order_detail', order_id=order_id)

    return render(request, 'order/close.html', {
        'title': _('Close %(order)s') % {
            'order': str(order)
        },
    })
