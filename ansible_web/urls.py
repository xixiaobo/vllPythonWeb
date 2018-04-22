from django.conf.urls import *
from django.contrib import admin

from ansible_web import views
admin.autodiscover()

urlpatterns = [
    url(r'api/rest/QueryHost',views.QueryHost),
    url(r'api/rest/PingHost',views.ping),
    url(r'api/rest/SysstatHost',views.sysstat),
    url(r'api/rest/StatusHost',views.statusHost),
    url(r'api/rest/CurrencyHost',views.currency),
]