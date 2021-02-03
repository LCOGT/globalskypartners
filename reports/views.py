from .models import *
from .forms import *
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction

class ReportCreate(CreateView):
    model = Report
    template_name = 'reports/report_create.html'
    form_class = ReportForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ReportCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['titles'] = ReportFormSet(self.request.POST)
        else:
            data['titles'] = ReportFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        titles = context['titles']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if titles.is_valid():
                titles.instance = self.object
                titles.save()
        return super(ReportCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reports:report_detail', kwargs={'pk': self.object.pk})
