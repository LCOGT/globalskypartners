from django.db import models

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

    def __str__(self):
        return self.year

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
    proposal = models.CharField(max_length=50, unique=True)
    pi = models.CharField(max_length=100)
    pi_email = models.EmailField()
    summary = models.TextField()
    cohorts = models.ManyToManyField(Cohort)
    active = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    region = models.ManyToManyField(Region,blank=True)
    program = models.ManyToManyField(ProgramType, blank=True)

    def __str__(self):
        if self.active:
            state = f"({self.proposal})"
        elif self.rejected:
            state = "[REJECTED]"
        else:
            state = "[INACTIVE]"
        return f"{self.name} {state}"

    class Meta:
        ordering = ('name',)
