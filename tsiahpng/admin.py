from django.contrib import admin

from . import models


@admin.register(models.Shop, models.Category)
class BasicAdmin(admin.ModelAdmin):
    ...


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
        'is_active',
    ]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = ['shop']
    list_display = ['id', 'alias', 'shop', 'is_open', 'is_active']


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_filter = ['user', 'order']
    list_display = ['id', 'order', 'user', 'item', 'quantity', 'price']


@admin.register(models.SummaryTemplate)
class SummaryTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'alias', 'is_active']
