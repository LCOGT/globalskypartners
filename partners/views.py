from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.list import ListView

from .models import Partner, Semester, Cohort, Proposal
from .forms import ProposalForm, PartnerForm, BulkUploadUsers

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

class LoginViewCustom(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activecall'] = Cohort.objects.filter(active_call=True)
        return context

class PartnerList(ListView):
    model = Partner
    queryset = Partner.objects.filter(active=True).order_by('name')

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        if year := self.request.GET.get('year', None):
            cohort = Cohort.objects.get(year=year)
            qs = Partner.objects.filter(cohorts=cohort).order_by('name').annotate(num_reports=Count('report',filter=Q(report__period=cohort)))
            return qs
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if year := self.request.GET.get('year', None):
            cohort = Cohort.objects.get(year=year)
            context['semesters'] = list(cohort.semester_set.all().values_list('code', flat=True))
            context['title'] = f"{year} Partners"
            context['proposals'] = list(Partner.objects.filter(cohorts=cohort).values_list('proposal_code', flat=True))
        else:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        semester = Semester.objects.get(start__lte=now, end__gte=now)
        context['datestamp'] = semester.start.isoformat(' ')[:19]
        if self.request.user in self.object.pi.all():
            context['owner'] = True
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

class ProposalDetail(LoginRequiredMixin, UserPassesTestMixin,  DetailView):
    model = Proposal

    def test_func(self):
        return self.get_object().submitter == self.request.user

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

class ProposalEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'partners/proposal_form.html'

    def test_func(self):
        return self.get_object().submitter == self.request.user

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

class ProposalSubmit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Proposal

    def test_func(self):
        return self.get_object().submitter == self.request.user

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = 1 #Submitted
        obj.save()
        messages.success(request, 'Proposal "{}" submitted'.format(obj.partner.name))
        obj.email_conf()
        return redirect(reverse_lazy('partners'))

class PartnerEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partners/partner_form.html'
    slug_field = 'proposal_code'
    slug_url_kwarg = 'proposal_code'

    def test_func(self):
        return self.request.user in self.get_object().pi.all()

    def get_success_url(self):
        return reverse_lazy('partner', kwargs={'proposal_code':self.object.proposal_code})

class ProposalPDFView(LoginRequiredMixin, UserPassesTestMixin,  DetailView):
    model = Proposal

    def test_func(self):
        return self.get_object().submitter == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ProposalForm(instance=context['object'], user=self.request.user)
        form.fields.pop('title')
        form.fields.pop('summary')
        form.fields.pop('new_or_old')
        form.fields.pop('title_options')
        context['proposal'] = form
        return context

    def render_to_response(self, context, **kwargs):
        context['pdf'] = True
        pdf_response = HttpResponse(content_type='application/pdf')
        pdf = self.object.generate_pdf()

        pdf_response.write(pdf)
        filename = f"proposal-{self.object.id}.pdf"
        pdf_response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return pdf_response

class UploadUserView(FormView):
    template_name = 'partners/user_upload.html'
    form_class = BulkUploadUsers
    success_url = reverse_lazy('user-upload')

    def get_form_kwargs(self):
        kwargs = super(UploadUserView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['token'] = self.request.session['token']
        return kwargs

    def form_valid(self, form):
        error = None
        try:
            form.upload_to_portal()
        except ValidationError as e:
            error = e
        return render(self.request, self.template_name,{'error':error,'form':form, 'users':form.users})
