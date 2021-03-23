from django.contrib import admin
from django.urls import path, include

from .views import PartnerList, PartnerDetail, ProposalCreate

urlpatterns = [
    path('', PartnerList.as_view(), name='partners'),
    path('apply', ProposalCreate.as_view(), name='apply'),
    path('<slug:proposal_code>', PartnerDetail.as_view(), name='partner')
]
