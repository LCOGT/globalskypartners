import io

from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
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
    (3, 'Rejected')
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

    def __str__(self):
        if self.active_call:
            return f"{self.year} active"
        return f"{self.year}"

    class Meta:
        ordering = ('year',)

    def save(self, *args, **kwargs):
        if not self.active_call:
            return super(Cohort, self).save(*args, **kwargs)
        with transaction.atomic():
            Cohort.objects.filter(active_call=True).update(active_call=False)
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

    def __str__(self):
        return f"{self.partner} {self.cohort}"

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
            if f.editable and value and f.name not in ('id', 'status', 'partner', 'cohort','submitter') :
                if f.name in ('time','size'):
                    val = value
                else:
                    val = markdown.markdown(value)
                fields.append(
                  {
                   'label':f.verbose_name,
                   'name':f.name,
                   'value':val,
                  }
                )
        return fields

    def generate_pdf(self, no_trans=False, path=''):
        context = {
            'id' : f"EPO-{self.cohort.year}-{self.id}",
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
