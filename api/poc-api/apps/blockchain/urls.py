# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from rest_framework.routers import url

from apps.blockchain.views import (
    TransactionListView
)

app_name = 'additional_data'


urlpatterns = [
    url('^transactions/$', TransactionListView.as_view())
]
