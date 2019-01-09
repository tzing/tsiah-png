from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('', views.overview, name='list'),
    path('<int:passbook_id>/', views.detail, name='detail'),
    path('<int:passbook_id>/add/', views.add, name='add'),
]
