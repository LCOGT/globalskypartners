import sys
import csv

from django.core.management.base import CommandError, BaseCommand

from partners.models import Cohort, Partner
from reports.models import Report

class Command(BaseCommand):
    """
    Import old report spreadsheets
    """

    help = 'Import old report spreadsheets'
    def add_arguments(self, parser):
        parser.add_argument("-c", "--cohort", dest="cohort",help='reporting cohort', type=str)
        parser.add_argument("-f", "--file", dest="file",help='file path for ingest', type=str)

    def handle(self, **options):
        try:
            cohort = Cohort.objects.get(year=options.get("cohort"))
        except:
            sys.stderr.write(f'No cohort matching {options.get("cohort")}\n')
            sys.exit(0)
        filename = options.get("file")
        with open(filename,'r') as f:
            partnersreader = csv.reader(f, delimiter=',', quotechar='"',skipinitialspace=True)
            for row in partnersreader:
                partner = Partner.objects.get(name=row[1])
                report, new = Report.object.get_or_create(partner=partner, cohort=cohort)
                if new:
                    sys.stdout.write(f'Adding {row[0]}\n')
                    # Only change the basic info for new partners
                    for k, v in {0:'name', 4:'summary', 2:'pi', 3:'pi_email'}.items():
                        setattr(partner, v, row[k])
                else:
                    sys.stdout.write(f'Updating {row[0]}\n')
                partner.active = True
                partner.semesters.add(semester)
                partner.save()
