from django.urls import path

import api.apis as api
import tsiahpng.apis as tsiahpng

app_name = 'api'

urlpatterns = [
    # user
    path('users', api.query_users, name='users'),

    # order
    path(
        'order/<int:order_id>/summary',
        tsiahpng.summary_order,
        name='order_summary'),
]
