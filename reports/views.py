import csv
from collections import Counter

from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django_countries import countries

from .models import *
from .forms import *
from .plots import cohort_countries, get_partner_counts, breakdown_per_partner, \
    choropleth_map, get_partner_sum, meta_plot


class PassUserMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ReportList(LoginRequiredMixin, ListView):
    model = Report

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ReportList, self).get_context_data(**kwargs)
        context['impacts'] = Imprint.objects.filter(report__created_by=self.request.user, report__status=0)
        if years := Cohort.objects.filter(active_report=True).values_list('year',flat=True):
            context['active_report'] = years
        if self.request.user.is_staff:
            context['all_reports'] = Report.objects.all().order_by('period','partner__name')
        return context

class ImpactCreate(LoginRequiredMixin, PassUserMixin, CreateView):
    form_class = ImpactForm
    template_name = 'reports/imprint_create.html'
    success_url = reverse_lazy('report-list')

    def form_valid(self, form):
        partner = Partner.objects.get(id=form.cleaned_data.get("partner"))
        now = timezone.now()
        cohorts = [c for c in Cohort.objects.all() if c.start <= now and c.end >= now ]
        report, created = Report.objects.get_or_create(partner=partner, period=cohorts[0], created_by = self.request.user)
        form.instance.report = report
        return super().form_valid(form)

class ReportCreate(LoginRequiredMixin, PassUserMixin, CreateView):
    form_class = ReportForm
    model = Report
    template_name = 'reports/report_create.html'


    def form_valid(self, form):
        context = self.get_context_data()
        # impacts = context['impacts']

        form.instance.created_by = self.request.user
        form.instance.period = Cohort.objects.get(active_report=True)
        self.object = form.save()
        return super(ReportCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('report-add-impact', kwargs={'pk':self.object.id})

class ReportAddImpact(LoginRequiredMixin, PassUserMixin, CreateView):
    form_class = ImpactForm
    model = Imprint
    template_name = 'reports/report_impact_create.html'

    def get_object(self):
        return Report.objects.get(id=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super(ReportAddImpact, self).get_form_kwargs()
        kwargs['report'] =self.get_object()
        return kwargs

    def get_context_data(self, *args, **kwargs):
        data = super(ReportAddImpact, self).get_context_data(**kwargs)
        data['impacts'] = Imprint.objects.filter(report=self.get_object())
        data['report'] = self.get_object()
        return data

    def form_valid(self, form):
        form.instance.report = self.get_object()
        return super(ReportAddImpact, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('report-add-impact', kwargs={'pk':self.get_object().id})

class DeleteImpact(LoginRequiredMixin, DeleteView):
    model = Imprint

    def get_success_url(self):
        return reverse_lazy('report-view', kwargs={'pk':self.get_object().report.id})

class ReportDetail(LoginRequiredMixin, DetailView):
    model = Report

    def get_context_data(self, *args, **kwargs):
        data = super(ReportDetail, self).get_context_data(**kwargs)
        data['impacts'] = Imprint.objects.filter(report=self.get_object())
        return data

class ReportEdit(LoginRequiredMixin, PassUserMixin, UpdateView):
    model = Report
    form_class= ReportForm

    def get_success_url(self):
        return reverse_lazy('report-add-impact', kwargs={'pk':self.get_object().id})

class ReportSubmit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report

    def test_func(self):
        return self.request.user in self.get_object().partner.pi.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = 1 #Submitted
        obj.save()
        messages.success(request, f'Report for "{obj.partner.name}" in {obj.period.year} submitted')
        return redirect(reverse_lazy('report-list'))

class FinalReport(LoginRequiredMixin, UserPassesTestMixin, View):

    template_name = 'reports/final_report.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        year = self.kwargs['year']
        cohort = Cohort.objects.get(year=year)
        reports = Report.objects.filter(period=cohort).annotate(subtotal=Sum('imprint__size')).order_by('partner__name')

        demos = Counter()
        demographics = Imprint.objects.filter(report__period=cohort)
        for d in demographics:
            demos.update({d.get_demographic_display():d.size})

        other = demographics.filter(demographic=99).exclude(demo_other__isnull=True).values_list('demo_other', flat=True)
        countries_dict, regions_dict = cohort_countries(year)

        return render(request, self.template_name,
                    {
                    'demographics'  : dict(demos),
                    'other_demos'   : ", ".join(other),
                    'total'         : Report.objects.filter(period=cohort).aggregate(total=Sum('imprint__size')),
                    'reports'       : reports,
                    'year'          : year,
                    'country_count' : len(countries_dict),
                    'regions'       : regions_dict,
                    'partner_data'  : get_partner_counts(reports),
                    'partner_counts': get_partner_sum(year),
                    'total_partners': Partner.objects.filter(cohorts=cohort).count(),
                    'map'           : choropleth_map(year),
                    'cit_science'   : Imprint.objects.filter(report__period__year=year, activity=7).aggregate(total=Sum('size'))
                    })


def countries_summary_view(request, year):
    countries_dict, regions_dict = cohort_countries(year)
    countries_dict = {countries.name(code=k): countries_dict[k] for k in sorted(countries_dict)}
    return render(request,'reports/countries.html', {'countries':countries_dict})
