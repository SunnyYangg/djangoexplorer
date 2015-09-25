from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseServerError
from report.actions import generate_report_action
from django.views.generic.base import View
from django.contrib.admin.views.decorators import staff_member_required
from report.models import Report
from report.forms import ReportForm


@staff_member_required
def download_report(request, report_id):
    try:
        report = Report.objects.get(pk=report_id)
        fn = generate_report_action()
        return fn(None, None, [report, ])
    except Report.DoesNotExist:
        raise Http404


class ReportView(View):

    def get(self, request, report_id):
        message = "Here is your report"

        report, form = self.get_instance_and_form(request, report_id, Http404)

        rows = request.GET.get('rows', None)
        if rows:
            pass
            #go get rows

        return self.render(request, report, form, message)

    def post(self, request, report_id):
        report, form = self.get_instance_and_form(request, report_id, HttpResponseServerError)
        message = "Report saved!" if form.save() else "There were errors while saving the report"
        return self.render(request, report, form, message)

    def get_instance_and_form(self, request, report_id, ex):
        try:
            report = Report.objects.get(pk=report_id)
        except Report.DoesNotExist:
            raise ex
        form = ReportForm(request.POST if len(request.POST) else None, instance=report)
        return report, form

    def render(self, request, report, form, message):
        c = RequestContext(request, {'report': report, 'form': form, 'message': message})
        return render_to_response('report/report.html', c)