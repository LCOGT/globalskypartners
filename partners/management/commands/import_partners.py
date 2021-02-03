import sys
import csv

from django.core.management.base import CommandError, BaseCommand

from partners.models import Partner, Semester

class Command(BaseCommand):
    """
    Fix pages where the stream field has not been corrected written
    """

    help = 'Fix pages where the stream field has not been corrected written'
    def add_arguments(self, parser):
        parser.add_argument("-c", "--code", dest="code",help='semester code', type=str)
        parser.add_argument("-f", "--file", dest="file",help='file path for ingest', type=str)

    def handle(self, **options):
        try:
            semester = Semester.objects.get(code=options.get("code"))
        except:
            sys.stderr.write(f'No semester matching {options.get("code")}\n')
            sys.exit(0)
        filename = options.get("file")
        with open(filename,'r') as f:
            partnersreader = csv.reader(f, delimiter=',', quotechar='"',skipinitialspace=True)
            for row in partnersreader:
                partner, new = Partner.objects.get_or_create(proposal=row[1])
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
