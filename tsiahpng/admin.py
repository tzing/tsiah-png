from django.contrib import admin
from django.contrib import auth
from django.utils.translation import gettext_lazy as _

from . import models


class TsiahPngAdminSite(admin.AdminSite):

    APP_ORDERING = {"auth": 10, "tsiahpng": 100, "account": 200}
    MODEL_ORDERING = {
        "WelcomeText": 50,
        "Category": 100,
        "Shop": 110,
        "Order": 120,
        "SummaryText": 180,
        "Passbook": 210,
        "Event": 220,
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


class ProductInline(admin.TabularInline):
    model = models.Product


class ShopAdmin(admin.ModelAdmin):
    list_display = ["__str__", "is_active", "changeable"]
    inlines = [ProductInline]


class TicketInline(admin.TabularInline):
    model = models.Ticket

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "item" and request.object:
            field.queryset = field.queryset.filter(shop=request.object.shop)
        return field


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

    inlines = [TicketInline]

    def get_form(self, request, obj=None, **kwargs):
        # save obj reference for future processing in Inline
        request.object = obj
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["shop"]
        else:
            return []

    def get_inline_instances(self, request, obj=None):
        if obj:
            return super().get_inline_instances(request, obj)
        return []


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
admin.site.register(models.Order, admin_class=OrderAdmin)
admin.site.register(models.WelcomeText, admin_class=WelcomeTextAdmin)
admin.site.register(models.SummaryText, admin_class=SummaryTextAdmin)

# customized admin
site = TsiahPngAdminSite(name="tsiahpng_admin")

site.register(auth.models.User, admin_class=auth.admin.UserAdmin)

site.register(models.Shop, admin_class=ShopAdmin)
site.register(models.Category)
site.register(models.Order, admin_class=OrderAdmin)
site.register(models.WelcomeText, admin_class=WelcomeTextAdmin)
site.register(models.SummaryText, admin_class=SummaryTextAdmin)
