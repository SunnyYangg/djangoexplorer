from django.conf.urls import patterns, url
from django.views.generic import ListView
from report.views import ReportView, CreateReportView, PlayReportView, DeleteReportView
from report.models import Report

urlpatterns = patterns('',
    url(r'(?P<report_id>\d+)/$', ReportView.as_view(), name='report_detail'),
    url(r'(?P<report_id>\d+)/download$', 'report.views.download_report', name='report_download'),
    url(r'(?P<pk>\d+)/delete$', DeleteReportView.as_view(), name='report_delete'),
    url(r'new/$', CreateReportView.as_view(), name='report_create'),
    url(r'play/$', PlayReportView.as_view(), name='report_playground'),
    url(r'$', ListView.as_view(model=Report), name='report_index'),
)