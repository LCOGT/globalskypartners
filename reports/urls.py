from django.urls import path, include

from .views import ReportCreate, ReportList, ImpactCreate, ReportEdit

urlpatterns = [
    path('impact/', ImpactCreate.as_view(), name='report-impact'),
    path('create/', ReportCreate.as_view(), name='report-create'),
    path('edit/', ReportEdit.as_view(), name='report-edit'),
    path('list/', ReportList.as_view(), name='report-list')
]
