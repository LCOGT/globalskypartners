from .models import *
from .forms import *

from crispy_forms.utils import render_crispy_form
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

# import plotly.express as px
# import pandas as pd

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

def audience_map(countries):
    world_path = Path(DATA_PATH) / 'custom.geo.json'
    with open(world_path) as f:
       geo_world = json.load(f)

    # Instanciating necessary lists
    found = []
    missing = []
    countries_geo = []

    # Looping over the custom GeoJSON file
    for country in geo_world['features']:

        # Country name detection
        country_name = country['properties']['name']

        # Checking if that country is in the dataset
        if country_name in countries:

            # Adding country to our "Matched/found" countries
            found.append(country_name)

            # Getting information from both GeoJSON file and dataFrame
            geometry = country['geometry']

            # Adding 'id' information for further match between map and data
            countries_geo.append({
                'type': 'Feature',
                'geometry': geometry,
                'id':country_name
            })

        # Else, adding the country to the missing countries
        else:
            missing.append(country_name)

    # Displaying metrics
    print(f'Countries found    : {len(found)}')
    print(f'Countries not found: {len(missing)}')
    geo_world_ok = {'type': 'FeatureCollection', 'features': countries_geo}

    df = pd.DataFrame({'zone':found, 'count':len(found) * [1]})

    fig = px.choropleth(
        df,
        geojson=geo_world_ok,
        locations='zone',
        color=df['count'],
        color_continuous_scale=["red"],
        coloraxis_showscale=False
    )

    fig.update(coloraxis_showscale=False)
    fig.show()
