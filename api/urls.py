from django.urls import path

import api.apis as api
import tsiahpng.apis as tsiahpng
import account.apis as account

app_name = 'api'

urlpatterns = [
    # user
    path('users', api.query_users, name='users'),

    # order
    path('order/<int:order_id>', tsiahpng.query_order, name='order_detail'),
    path(
        'order/<int:order_id>/summary',
        tsiahpng.summary_order,
        name='order_summary'),

    # passbook
    path('passbook', account.query_passbooks, name='passbooks')
]
