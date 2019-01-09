from django.contrib import admin

from . import models


@admin.register(models.Passbook)
class BasicAdmin(admin.ModelAdmin):
    ...


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = [
        'book',
        'related_order',
    ]

    list_display = [
        'id',
        'book',
        'title',
        'related_order',
    ]


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_filter = [
        'event',
        'user',
    ]

    list_display = [
        'id',
        'event',
        'user',
        'balance',
    ]
