from django.contrib import admin

import tsiahpng.admin

from . import models


class PassbookAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_active", "changeable"]


class EventAdmin(admin.ModelAdmin):
    list_display = ["__str__", "book", "related_order", "balance"]
    list_filter = ["book"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "event", "user", "balance"]
    list_filter = ["event", "user"]


# django admin
admin.site.register(models.Passbook, admin_class=PassbookAdmin)
admin.site.register(models.Event, admin_class=EventAdmin)
admin.site.register(models.Transaction, admin_class=TransactionAdmin)

# customized admin
tsiahpng.admin.site.register(models.Passbook, admin_class=PassbookAdmin)
tsiahpng.admin.site.register(models.Event, admin_class=EventAdmin)
tsiahpng.admin.site.register(models.Transaction, admin_class=TransactionAdmin)
