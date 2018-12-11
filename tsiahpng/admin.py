from django.contrib import admin

from . import models


@admin.register(models.Shop)
class ShopAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ['shop']
    list_display = ['name', 'shop']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        'shop',
        'category',
    ]

    list_display = [
        'name',
        'shop',
        'category',
        'price',
    ]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = ['shop']
    list_display = ['id', 'alias', 'shop']


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_filter = ['user', 'order']
    list_display = ['id', 'order', 'user', 'item', 'quantity', 'price']
