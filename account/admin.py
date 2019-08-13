from django.contrib import admin

import tsiahpng.admin

from . import models


class PassbookAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_active", "changeable"]


class TransactionInine(admin.TabularInline):
    model = models.Transaction


class EventAdmin(admin.ModelAdmin):
    list_display = ["__str__", "book", "related_order", "subtotal"]
    list_filter = ["book"]
    inlines = [TransactionInine]
    readonly_fields = ["subtotal"]


# django admin
admin.site.register(models.Passbook, admin_class=PassbookAdmin)
admin.site.register(models.Event, admin_class=EventAdmin)

# customized admin
tsiahpng.admin.site.register(models.Passbook, admin_class=PassbookAdmin)
tsiahpng.admin.site.register(models.Event, admin_class=EventAdmin)
