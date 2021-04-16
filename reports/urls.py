from django.urls import path, include

from .views import ReportCreate, ReportList

urlpatterns = [
    path('create/', ReportCreate.as_view(), name='report-create'),
    path('list/', ReportList.as_view(), name='report-list')
]
