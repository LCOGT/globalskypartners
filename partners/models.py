import io
import re
from pathlib import Path
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core.mail import send_mail
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML, CSS
import markdown


REGION_CHOICES = (
    (0, 'Online Only'),
    (1, 'Europe'),
    (2, 'Asia'),
    (3, 'Latin America and Caribean'),
    (4, 'Northern Africa'),
    (5, 'Sub-Saharan Africa'),
    (6, 'Middle East'),
    (7, 'Oceania'),
    (8, 'Northern America')
)

PROGRAM_CHOICES = (
    (0, 'In-person workshops/training/mentoring'),
    (1, 'Online workshops/training/mentoring'),
    (2, 'General audience'),
    (3, 'Citizen science')
)

AUDIENCE_SIZE = (
    (0, 'Small (<50)'),
    (1, 'Medium (50 - 200)'),
    (2, 'Large (200 - 1000)'),
    (3, 'Very large (> 1000)')
)

STATUS = (
    (0, 'Draft'),
    (1, 'Submitted'),
    (2, 'Accepted'),
    (3, 'Rejected'),
    (4, 'Synced to Portal')
)

class Region(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.name}"

class ProgramType(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.name}"

class Cohort(models.Model):
    year = models.CharField(max_length=4)
    active_call = models.BooleanField(default=False)
    deadline = models.DateTimeField(default=timezone.now)
    call = models.URLField(blank=True)
    proposalfile = models.FileField(upload_to='proposals', blank=True)
    active_report = models.BooleanField(default=False)
    call_id = models.CharField("ID of call in obs portal", max_length=20, blank=True, null=True)


    def __str__(self):
        if self.active_call:
            return f"{self.year} active"
        return f"{self.year}"

    @property
    def start(self):
        try:
            return min(self.semester_set.all().values_list('start', flat=True))
        except ValueError:
            return timezone.now()

    @property
    def end(self):
        try:
            return max(self.semester_set.all().values_list('end', flat=True))
        except ValueError:
            return timezone.now()

    @property
    def label(self):
        return f'{self.start.year} - {self.end.year}'

    class Meta:
        ordering = ('year',)

    def save(self, *args, **kwargs):
        if self.active_call or self.active_report:
            with transaction.atomic():
                if self.active_call:
                    Cohort.objects.filter(active_call=True).update(active_call=False)
                if self.active_report:
                    Cohort.objects.filter(active_report=True).update(active_report=False)
                return super(Cohort, self).save(*args, **kwargs)
        else:
            return super(Cohort, self).save(*args, **kwargs)


class Semester(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    code = models.CharField(max_length=6)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code}"

    class Meta:
        ordering = ('start',)

class Partner(models.Model):
    name = models.CharField(max_length=200)
    proposal_code = models.CharField(max_length=50, blank=True)
    summary = models.TextField(blank=True)
    cohorts = models.ManyToManyField(Cohort, blank=True)
    active = models.BooleanField(default=False)
    region = models.ManyToManyField(Region,blank=True)
    program = models.ManyToManyField(ProgramType, blank=True)
    pi = models.ManyToManyField(User, blank=True, through='Membership')

    def is_pending(self):
        if self.proposal_code:
            return False
        else:
            return True

    def __str__(self):
        if self.active:
            state = f"({self.proposal_code})"
        else:
            state = "[INACTIVE]"
        return f"{self.name} {state}"

    class Meta:
        ordering = ('name',)

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} leads {self.partner}"


class Proposal(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    people = models.TextField('people involved in coordinating the project')
    institution = models.CharField('supporting institution or organization',max_length=120)
    description = models.TextField('project description')
    use = models.TextField('how will this project make use of LCO’s unique capabilities?')
    experience = models.TextField('what experience do you have of running educational programs')
    size = models.PositiveSmallIntegerField(choices=AUDIENCE_SIZE)
    support = models.TextField('how will you support your users?')
    help = models.TextField('what help do you need from LCO in setting up your project?')
    time = models.IntegerField('hours requested')
    time_reason = models.TextField('justification of time requested')
    comments = models.TextField('any comments', blank=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=0)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.partner} {self.cohort}"

    def save(self, *args, **kwargs):
        # give the proposal a code if it doesn't have one
        if not self.code:
            self.code = self.generate_code()
        super(Proposal, self).save(*args, **kwargs)
    
    def generate_code(self):
        cohort = self.cohort.year
        number = Proposal.objects.filter(cohort=self.cohort).count() + 1
        return f"{cohort}-{number}"

    @property
    def title(self):
        return self.partner.name

    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = []
        for f in self._meta.get_fields():

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr(self, get_choice):
                value = getattr(self, get_choice)()
            else:
                try:
                    value = getattr(self, fname)
                except AttributeError:
                    value = None

            # only display fields with values and skip some fields entirely
            if f.editable and value and f.name not in ('id', 'status', 'partner', 'cohort','submitter', 'code','hours') :
                if f.name in ('time','size'):
                    val = value
                else:
                    val = mark_safe(markdown.markdown(value))
                fields.append(
                  {
                   'label':f.verbose_name,
                   'name':f.name,
                   'value':val,
                  }
                )
        return fields

    def generate_pdf(self, no_trans=False):
        context = {
            'object': self,
            'pdf': True,
            'no_trans' : no_trans,
            'media_root' : settings.MEDIA_ROOT,
            'proposal' : self.get_all_fields()
        }
        with open(finders.find('css/print.css')) as f:
            css = CSS(string=f.read())
        html_string = render_to_string('partners/proposal_print.html', context)
        html = HTML(string=html_string, base_url="https://partners.lco.global")
        # filepath = Path(path) / filename
        fileobj = io.BytesIO()
        html.write_pdf(fileobj, stylesheets=[css])
        # return filepath
        pdf = fileobj.getvalue()
        fileobj.close()
        return pdf

    def save_pdf(self, path=''):
        name = f"EPO-{self.cohort.year}-{self.id}.pdf"
        filepath = Path(path) / name
        fileobj = self.generate_pdf()
        with open(filepath, 'wb') as fp:
            fp.write(fileobj)
        return filepath

    def email_conf(self):
        review_end = self.cohort.deadline + timedelta(weeks=3)
        params = {
                'title' : self.partner.name,
                'first_name' : self.submitter.first_name,
                'year' : self.cohort.year,
                'date' : review_end,
                'startdate' : self.cohort.deadline,
                'id'   : self.id
                }
        msg = render_to_string('partners/email_submission.txt', params)
        send_mail(
                f'Global Sky Partners submission {self.cohort.year}',
                msg,
                'portal@lco.global',
                [self.submitter.email],
            )

class Review(models.Model):
    REJECTED = 0
    ACCEPTED = 1
    QUESTIONS = 2
    PENDING = 3
    VERDICT = (
        (PENDING,'Verdict Pending'),
        (REJECTED, 'Rejected'),
        (ACCEPTED, 'Accepted'),
        (QUESTIONS, 'Further Questions'),
    )
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    verdict = models.PositiveSmallIntegerField(choices=VERDICT, default=3)
    hours = models.FloatField(help_text='hours awarded', default=0.0)
    emailed = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True)
    rank = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        if self.verdict in [0,1]:
            verb = 'was'
        elif self.verdict == 3:
            verb = 'is'
        else:
            verb = 'has'
        return f'{self.proposal.partner.name} in {self.proposal.cohort.year} {verb} {self.verdict}'

    def email_verdict(self):
        params = {
                'title' : self.proposal.partner.name,
                'first_name' : self.proposal.submitter.first_name,
                'year' : self.proposal.cohort.year,
                'hours'   : self.hours,
                'comments' : self.comments,
                'verdict' : self.verdict
                }
        msg = render_to_string('partners/email_verdict.txt', params)
        send_mail(
                f'Global Sky Partners panel verdict {self.proposal.partner.name}',
                msg,
                'portal@lco.global',
                [self.proposal.submitter.email],
            )