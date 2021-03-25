from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

from .models import Partner, Semester, Cohort, Proposal
from .forms import ProposalForm

@login_required
def home(request):
    now = datetime.now()
    cohort = Semester.objects.get(start__lte=now, end__gte=now).cohort
    proposals = list(Partner.objects.filter(active=True).values_list('proposal_code', flat=True))
    semesters = list(cohort.semester_set.all().values_list('code', flat=True))
    return render(request, 'home.html',{'proposals':proposals,'semesters':semesters})


class PartnerList(ListView):
    model = Partner
    queryset = Partner.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        semester = Semester.objects.get(start__lte=now, end__gte=now)
        context['semester'] = semester.code
        return context

class PartnerDetail(DetailView):
    model = Partner
    slug_field = 'proposal_code'
    slug_url_kwarg = 'proposal_code'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        semester = Semester.objects.get(start__lte=now, end__gte=now)
        context['datestamp'] = semester.start.isoformat(' ')[:19]
        return context

class ProposalList(LoginRequiredMixin, ListView):
    model = Proposal

    def get_queryset(self):
        user = self.request.user
        return Proposal.objects.filter(partner__submitter=user)

class ProposalDetail(LoginRequiredMixin, DetailView):
    model = Proposal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ProposalForm(instance=context['object'], user=self.request.user)
        form.fields.pop('title')
        form.fields.pop('summary')
        context['proposal'] = form
        return context

class ProposalCreate(LoginRequiredMixin, CreateView):
    form_class = ProposalForm
    template_name = 'partners/proposal_form.html'
    success_url = reverse_lazy('partners')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exclusions'] = ['title','title_options','summary','institution','time','size']
        return context

    def get_form_kwargs(self):
        kwargs = super(ProposalCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        form.instance.cohort = Cohort.objects.get(active_call=True)
        form.instance.partner = form.cleaned_data['partner']
        form.instance.status = 1
        return super().form_valid(form)
