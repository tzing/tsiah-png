from django.urls import path, include

from . import views

app_name = "account"

urlpatterns = [
    path("", views.account_list, name="list"),
    path("<int:passbook_id>/", views.account_detail, name="detail"),
    path("<int:passbook_id>/add", views.create_event, name="create_event"),
]
