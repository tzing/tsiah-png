from django.contrib import admin
from django.contrib import auth
from django.utils.translation import gettext_lazy as _

from . import models


class TsiahPngAdminSite(admin.AdminSite):

    APP_ORDERING = {"auth": 10, "tsiahpng": 100}
    MODEL_ORDERING = {
        "WelcomeText": 50,
        "Shop": 110,
        "Category": 111,
        "Product": 112,
        "Order": 120,
        "Ticket": 121,
        "SummaryText": 180,
    }

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)

        # Sort the apps
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
        app_list = sorted(
            app_list, key=lambda x: self.APP_ORDERING.get(x["app_label"], 999)
        )

        # Sort the models within each app.
        for app in app_list:
            app["models"].sort(key=lambda x: x["name"])
            app["models"].sort(
                key=lambda x: self.MODEL_ORDERING.get(x["object_name"], 999)
            )

        return app_list


class ShopAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_active", "changeable"]


class ProductAdmin(admin.ModelAdmin):
    list_filter = ["shop", "category"]
    list_display = ["name", "shop", "category", "price", "is_active"]


class OrderAdmin(admin.ModelAdmin):
    list_filter = ["shop"]
    list_display = [
        "__str__",
        "shop",
        "is_available",
        "is_active",
        "sum_quantity",
        "sum_cost",
    ]


class TicketAdmin(admin.ModelAdmin):
    list_filter = ["user", "order"]
    list_display = ["__str__", "order", "user", "cost"]


class WelcomeTextAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_active"]


class SummaryTextAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_active"]

    change_form_template = "tsiahpng/admin/summary_text.pug"

    class Media:
        css = {"all": ("tsiahpng/admin/summary_text.css",)}


# django admin
admin.site.register(models.Shop, admin_class=ShopAdmin)
admin.site.register(models.Category)
admin.site.register(models.Product, admin_class=ProductAdmin)
admin.site.register(models.Order, admin_class=OrderAdmin)
admin.site.register(models.Ticket, admin_class=TicketAdmin)
admin.site.register(models.WelcomeText, admin_class=WelcomeTextAdmin)
admin.site.register(models.SummaryText, admin_class=SummaryTextAdmin)

# customized admin
site = TsiahPngAdminSite(name="tsiahpng_admin")

site.register(auth.models.User)

site.register(models.Shop, admin_class=ShopAdmin)
site.register(models.Category)
site.register(models.Product, admin_class=ProductAdmin)
site.register(models.Order, admin_class=OrderAdmin)
site.register(models.Ticket, admin_class=TicketAdmin)
site.register(models.WelcomeText, admin_class=WelcomeTextAdmin)
site.register(models.SummaryText, admin_class=SummaryTextAdmin)
