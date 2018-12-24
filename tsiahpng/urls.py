import uuid

from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

from . import views

stage_id = uuid.uuid4()  # workaround for translation version

urlpatterns = [
    path('', views.homepage, name='homepage'),

    # menu
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/<int:shop_id>', views.menu_detail, name='menu_detail'),
    path('menu/add/<int:shop_id>', views.menu_add, name='menu_add'),

    # order
    path('order/', views.order_list, name='order_list'),
    path('order/new/', views.order_create, name='order_create'),
    path('order/<int:order_id>', views.order_detail, name='order_detail'),
    path('order/<int:order_id>-close', views.order_close, name='order_close'),

    # api
    path(
        'api/summary/<int:order_id>',
        views.order_summary,
        name='api_summary_string'),

    # i18n
    path(
        'jsi18n/',
        cache_page(86400, key_prefix=f'jsi18n-{stage_id.hex}')(
            JavaScriptCatalog.as_view(packages=['tsiahpng'])),
        name='javascript-catalog'),
]
