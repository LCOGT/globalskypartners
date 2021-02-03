from django.contrib import admin
from django.urls import path, include

from .views import PartnerList, PartnerDetail

urlpatterns = [
    path('list', PartnerList.as_view(), name='partners'),
    path('<slug:proposal>', PartnerDetail.as_view(), name='partner')
]
