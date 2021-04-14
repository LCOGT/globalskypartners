from django.contrib import admin
from django.urls import path, include

from .views import PartnerList, PartnerDetail, ProposalCreate, ProposalList, ProposalDetail, \
    ProposalEdit, ProposalSubmit

urlpatterns = [
    path('', PartnerList.as_view(), name='partners'),
    path('apply/', ProposalCreate.as_view(), name='apply'),
    path('proposals/',ProposalList.as_view(), name='proposals'),
    path('proposal/<int:pk>/',ProposalDetail.as_view(), name='proposal'),
    path('proposal/<int:pk>/edit/',ProposalEdit.as_view(), name='proposal-edit'),
    path('proposal/<int:pk>/submit/',ProposalSubmit.as_view(), name='proposal-submit'),
    path('<slug:proposal_code>/', PartnerDetail.as_view(), name='partner')
]
