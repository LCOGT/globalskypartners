from django.db import models

from partners.models import Partner, Cohort

AUDIENCE_CHOICES = (
    (0,'Elementary school students'),
    (1,'High school students'),
    (2,'Teachers'),
    (3,'Families'),
    (4,'General Public'),
    (5, 'Adult learners')
)

DEMOGRAPH_CHOICES = (
    (0, 'Under-served or under-represented'),
    (1, 'Developing world'),
    (2, 'Well served communities')
)

ACTIVITY_CHOICES = (
    (0, 'Student workshops'),
    (1, 'Teacher workshops'),
    (2, 'School workshops'),
    (3, 'Online school workshops'),
    (4, 'Student mentoring'),
    (5, 'Student research'),
    (6, 'Beginners tutorials'),
    (7, 'Citizen Science'),
    (8, 'Artistic project')
)

class Report(models.Model):
    partner = models.ForeignKey(Partner)
    period = models.ForeignKey(Cohort)
    countries = CountryField(multiple=True)
    summary = models.TextField('summary of activity')
    comment = models.TextField('comments')

    def __str__(self):
        return f"{self.partner.name} {self.period}"


class Imprint(models.Model):
    size = models.IntegerField()
    audience = models.SmallPositiveInteger(choices=AUDIENCE_CHOICES)
    activity = models.SmallPositiveInteger('type of activity',choices=ACTIVITY_CHOICES)
    demographic = models.SmallPositiveInteger('audience demographic',choices=DEMOGRAPH_CHOICES)
    demo_other = models.TextField('other demographic', blank=True)
    impact = models.TextField('primary impact', blank=True)
    report = models.ForeignKey(Report)

class Product(models.Model):
    description = models.TextField('description of product')
    link = models.URLField(blank=True)
    report = models.ForeignKey(Report)
