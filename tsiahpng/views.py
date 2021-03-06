import collections
import random

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import TemplateSyntaxError
from django.utils import timezone

from django.contrib import messages
from django.utils.translation import gettext as _

from . import default
from . import forms
from . import models
from . import settings
from . import utils


def homepage(request):
    context = {
        "messages": messages.get_messages(request),
        "order_status_alterable": settings.ALLOW_ANYONE_ALTER_ORDER_STATUS,
        "recent_orders": models.Order.objects.filter(is_active=True)[
            : settings.MAX_RECENT_ORDERS
        ],
    }

    # welcome string
    if models.WelcomeText.objects.exists():
        welcome = random.choice(models.WelcomeText.objects.filter(is_active=True))
        context.update(title=welcome.title, subtitle=welcome.subtitle)
    else:
        context.update(title=_("Welcome"), subtitle=None)

    # available orders
    today = timezone.localtime().date()
    available_orders = models.Order.objects.filter(
        is_active=True, is_available=True, order_date__gte=today
    )

    if available_orders:
        context.update(
            available_orders=available_orders, **utils.get_stuff_ordering(request)
        )

    return render(request, "tsiahpng/homepage.pug", context)


def shop_list(request):
    shops = models.Shop.objects.filter(is_active=True)

    idx_page = utils.try_parse(request.GET.get("p"), 1)
    paginator = Paginator(shops, settings.SHOP_PER_PAGE)

    return render(
        request,
        "tsiahpng/menu/index.pug",
        {
            "title": _("Menu"),
            "shops": paginator.get_page(idx_page),
            "messages": messages.get_messages(request),
        },
    )


def shop_detail(request, shop_id):
    # get shop
    try:
        shop = models.Shop.objects.get(id=shop_id, is_active=True)
    except models.Shop.DoesNotExist:
        messages.error(request, _("Shop #{id} not exists.").format(id=shop_id))
        return redirect("tsiahpng:shop_list")

    # organize products
    sorted_products = collections.OrderedDict()
    for category in shop.related_categories():
        sorted_products[category] = shop.products(category=category)

    unsorted_products = shop.products(category=None)
    if unsorted_products:
        sorted_products[None] = unsorted_products

    # recent orders
    orders = models.Order.objects.filter(shop=shop, is_active=True)[
        : settings.MAX_RECENT_ORDERS
    ]

    return render(
        request,
        "tsiahpng/menu/detail.pug",
        {
            "title": str(shop),
            "shop": shop,
            "messages": messages.get_messages(request),
            "related_products": sorted_products,
            "recent_orders": orders,
        },
    )


def shop_add_product(request, shop_id):
    # get shop
    try:
        shop = models.Shop.objects.get(id=shop_id, is_active=True)
    except models.Shop.DoesNotExist:
        messages.error(request, _("Shop #{id} not exists.").format(id=shop_id))
        return redirect("tsiahpng:shop_list")

    # check permission
    if not shop.changeable:
        messages.error(request, _("{shop} is not changeable.").format(shop=shop))
        return redirect("tsiahpng:shop_detail", shop_id=shop_id)

    # form
    if request.method == "POST" and utils.is_new_post(request):
        form = forms.CreateProductForm(request.POST)
        prod = form.to_model()
        if prod:
            messages.success(request, _("Successfully add {prod}.").format(prod=prod))
            request.session[f"shop_add_product/{shop.id}/price"] = prod.price
            request.session[f"shop_add_product/{shop.id}/category"] = (
                prod.category.id if prod.category else None
            )
            return redirect("tsiahpng:shop_add_product", shop_id=shop_id)
        else:
            messages.error(request, _("Invalid requests."))

    # render
    return render(
        request,
        "tsiahpng/menu/add_product.pug",
        {
            "title": _("Add product to {shop}").format(shop=shop),
            "shop": shop,
            "categories": models.Category.objects.all(),
            "default_product_price": request.session.get(
                f"shop_add_product/{shop.id}/price", settings.DEFAULT_PROD_PRICE
            ),
            "last_category": request.session.get(
                f"shop_add_product/{shop.id}/category", -1
            ),
            "messages": messages.get_messages(request),
        },
    )


def order_list(request):
    orders = models.Order.objects.filter(is_active=True)

    idx_page = utils.try_parse(request.GET.get("p"), 1)
    paginator = Paginator(orders, settings.ORDER_PER_PAGE)

    return render(
        request,
        "tsiahpng/order/index.pug",
        {
            "title": _("Order"),
            "orders": paginator.get_page(idx_page),
            "messages": messages.get_messages(request),
            "status_alterable": settings.ALLOW_ANYONE_ALTER_ORDER_STATUS,
        },
    )


def order_detail(request, order_id):
    # get order
    try:
        order = models.Order.objects.get(id=order_id, is_active=True)
    except models.Order.DoesNotExist:
        messages.error(request, _("Order #{id} id not exists.").format(id=order_id))
        return redirect("tsiahpng:order_list")

    # form
    if request.method == "POST" and utils.is_new_post(request):
        form = forms.OrderingForm(request.POST)
        tickets = form.to_models()
        if tickets:
            user = tickets[-1].user

            msg = _("{user} ordered {items}; ${price:,} in total.").format(
                user=utils.get_username(user),
                items=", ".join(str(t) for t in tickets),
                price=sum(t.cost for t in tickets),
            )
            messages.success(request, msg)

            request.session["ordering/last_user"] = user.id
        else:
            messages.error(request, _("Invalid requests."))

    return render(
        request,
        "tsiahpng/order/detail.pug",
        {
            "title": str(order),
            "order": order,
            "summary_template": models.SummaryText.objects.filter(is_active=True),
            "closable": order.is_available and settings.ALLOW_ANYONE_ALTER_ORDER_STATUS,
            **utils.get_stuff_ordering(request),
        },
    )


def order_create(request):
    if not settings.ALLOW_ANYONE_ALTER_ORDER_STATUS:
        messages.error(_("No enough permission for this operation."))
        return redirect("tsiahpng:shop_detail")

    # post request
    if request.method == "POST" and utils.is_new_post(request):
        form = forms.CreateOrderForm(request.POST)
        order = form.to_model()
        if order:
            messages.success(
                request, _('Successfully create order "{order}".').format(order=order)
            )
            request.session["order_create/last_shop"] = order.shop.id
            return redirect("tsiahpng:order_detail", order.id)
        else:
            messages.error(request, _("Invalid requests."))

    return render(
        request,
        "tsiahpng/order/create_order.pug",
        {
            "title": _("Create order"),
            "shops": models.Shop.objects.filter(is_active=True),
            "default_date": default.default_order_date(),
            "last_shop": request.session.get("order_create/last_shop"),
            "messages": messages.get_messages(request),
        },
    )


def order_close(request, order_id):
    if request.method == "POST" and utils.is_new_post(request):
        # get order
        try:
            order = models.Order.objects.get(id=order_id, is_active=True)
        except models.Order.DoesNotExist:
            messages.error(request, _("Order #{id} id not exists.").format(id=order_id))
            return redirect("tsiahpng:order_list")

        # operate
        order.is_available = False
        order.save()

        messages.info(request, _("Order closed."))
        return redirect("tsiahpng:order_detail", order_id)

    return redirect("tsiahpng:order_detail", order_id)


def order_stringify(request, order_id):
    """Generate a summary text to the order.

    Query Parameters
    ----------------
        template (default: first template in db)
            id to the template
    """
    # get order
    try:
        order = models.Order.objects.get(id=order_id, is_active=True)
    except models.Order.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Order #{id} not exists.".format(id=order_id),
            },
            status=400,
        )

    # get template
    template_id = utils.try_parse(request.GET.get("template"), -1)
    if template_id == -1:
        return JsonResponse(
            {"success": False, "message": "Template id not specific or not valid."},
            status=400,
        )

    try:
        template = models.SummaryText.objects.get(id=template_id, is_active=True)
    except models.SummaryText.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Template #{id} not exists.".format(id=template_id),
            },
            status=400,
        )

    # render
    try:
        summary = template.render(order)
    except TemplateSyntaxError as e:
        args = ", ".join(e.args)
        return JsonResponse(
            {"success": False, "message": f"Template error: {args}"}, status=500
        )
    else:
        return JsonResponse({"success": True, "text": summary})


def error_404(request, exception=None, template_name="404.html"):
    return render(
        request,
        "tsiahpng/error.pug",
        {
            "title": _("Page Not Found"),
            "subtitle": _("Life is too short to be lost in such a small place."),
        },
        status=404,
    )


def error_500(request, *args, **argv):
    return render(
        request,
        "tsiahpng/error.pug",
        {"title": _("Internal Server Error"), "subtitle": _("Something goes wrong.")},
        status=404,
    )
