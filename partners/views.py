from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import Partner, Semester, Cohort, Proposal
from .forms import ProposalForm

@login_required
def home(request):
    now = datetime.now()
    partners = Partner.objects.filter(active=True, pi=request.user)
    semester = Semester.objects.get(start__lte=now, end__gte=now)
    return render(request, 'home.html',{'partners':partners,
                                        'semester':semester,
                                        'activecall':Cohort.objects.filter(active_call=True),
                                        'active_partners': Partner.objects.filter(active=True).count()
                                        })


class PartnerList(ListView):
    model = Partner
    queryset = Partner.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        semester = Semester.objects.get(start__lte=now, end__gte=now)
        cohort = Semester.objects.get(start__lte=now, end__gte=now).cohort
        context['semester'] = semester.code
        context['semesters'] = list(cohort.semester_set.all().values_list('code', flat=True))
        context['title'] = "Current Partners"
        context['proposals'] = list(Partner.objects.filter(active=True).values_list('proposal_code', flat=True))
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
        return Proposal.objects.filter(submitter=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if cohort := Cohort.objects.filter(active_call=True):
            context['activecall'] = cohort[0]
        return context

class ProposalDetail(LoginRequiredMixin, DetailView):
    model = Proposal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ProposalForm(instance=context['object'], user=self.request.user)
        form.fields.pop('title')
        form.fields.pop('summary')
        form.fields.pop('new_or_old')
        form.fields.pop('title_options')
        context['proposal'] = form
        return context

class ProposalCreate(LoginRequiredMixin, CreateView):
    form_class = ProposalForm
    template_name = 'partners/proposal_form.html'

    def get_success_url(self):
        return reverse_lazy('proposal', kwargs={'pk':self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if cohort := Cohort.objects.get(active_call=True):
            context['activecall'] = cohort
        context['exclusions'] = ['title','title_options','summary','institution','time','size','new_or_old']
        return context

    def get_form_kwargs(self):
        kwargs = super(ProposalCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        form.instance.cohort = Cohort.objects.get(active_call=True)
        form.instance.partner = form.cleaned_data['partner']
        form.instance.status = 0 # Draft
        return super().form_valid(form)

class ProposalEdit(LoginRequiredMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'partners/proposal_form.html'

    def get_success_url(self):
        return reverse_lazy('proposal', kwargs={'pk':self.object.pk})

    def get_form_kwargs(self):
        kwargs = super(ProposalEdit, self).get_form_kwargs()
        obj = self.get_object()
        kwargs.update({'user': self.request.user,'partner': obj.partner})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exclusions'] = ['title','title_options','summary','institution','time','size','new_or_old']
        if cohort := Cohort.objects.get(active_call=True):
            context['activecall'] = cohort
        context['editing'] = True
        return context

    def form_valid(self, form):
        form.instance.partner = form.cleaned_data['partner']
        return super().form_valid(form)

class ProposalSubmit(LoginRequiredMixin, UpdateView):
    model = Proposal

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = 1 #Submitted
        obj.save()
        messages.success(request, 'Proposal "{}" submitted'.format(obj.partner.name))
        return redirect(reverse_lazy('partners'))
