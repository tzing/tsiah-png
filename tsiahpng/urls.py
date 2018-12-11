from django.urls import path

from . import views

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
]
