from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import Partner, Semester

@login_required
def home(request):
    now = datetime.now()
    cohort = Semester.objects.get(start__lte=now, end__gte=now).cohort
    proposals = list(Partner.objects.filter(active=True).values_list('proposal', flat=True))
    semesters = list(cohort.semester_set.all().values_list('code', flat=True))
    return render(request, 'home.html',{'proposals':proposals,'semesters':semesters})


class PartnerList(ListView):
    model = Partner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        semester = Semester.objects.get(start__lte=now, end__gte=now)
        context['semester'] = semester.code
        return context

class PartnerDetail(DetailView):
    model = Partner
    slug_field = 'proposal'
    slug_url_kwarg = 'proposal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        semester = Semester.objects.get(start__lte=now, end__gte=now)
        context['datestamp'] = semester.start.isoformat(' ')[:19]
        return context
