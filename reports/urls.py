from django.urls import path, include

from .views import ReportCreate, ReportList, ImpactCreate, ReportEdit, \
    impact_create_api, ReportDetail, ReportAddImpact

urlpatterns = [
    path('impact/', ImpactCreate.as_view(), name='report-impact'),
    path('impact/api/', impact_create_api, name='report-impact-api'),
    path('create/', ReportCreate.as_view(), name='report-create'),
    path('<int:pk>/edit/', ReportEdit.as_view(), name='report-edit'),
    path('<int:pk>/impact/', ReportAddImpact.as_view(), name='report-add-impact'),
    path('<int:pk>/', ReportDetail.as_view(), name='report-view'),
    path('list/', ReportList.as_view(), name='report-list')
]
