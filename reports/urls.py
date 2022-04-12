from django.urls import path, include

from .views import ReportCreate, ReportList, ImpactCreate, ReportEdit, \
    ReportDetail, ReportAddImpact, DeleteImpact, ReportSubmit, FinalReport, \
    countries_summary_view

from .plots import meta_plot

urlpatterns = [
    path('impact/', ImpactCreate.as_view(), name='report-impact'),
    path('create/', ReportCreate.as_view(), name='report-create'),
    path('<int:pk>/edit/', ReportEdit.as_view(), name='report-edit'),
    path('<int:pk>/submit/', ReportSubmit.as_view(), name='report-submit'),
    path('<int:pk>/impact/', ReportAddImpact.as_view(), name='report-add-impact'),
    path('<int:pk>/impact/delete/', DeleteImpact.as_view(), name='impact-delete'),
    path('<int:pk>/', ReportDetail.as_view(), name='report-view'),
    path('list/', ReportList.as_view(), name='report-list'),
    path('final/<int:year>/', FinalReport.as_view(), name="final-report"),
    path('countries/<int:year>/', countries_summary_view, name="cohort_countries"),
    path('final/<int:year>/demo/<str:plotname>.png', meta_plot, name="meta_plot")
]
