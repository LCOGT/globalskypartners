from django.urls import path, include

from .views import ReportCreate

urlpatterns = [
    path('create/', ReportCreate.as_view(), name='create')
]
