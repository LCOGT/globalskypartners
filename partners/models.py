from django.db import models

from django.contrib.auth.models import User

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

    def __str__(self):
        if self.active_call:
            return f"{self.year} active"
        return f"{self.year}"

    class Meta:
        ordering = ('year',)

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
