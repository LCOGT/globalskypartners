
import sys
from django.core.files.base import ContentFile
from django.core.management.base import CommandError, BaseCommand

from partners.models import Proposal, Cohort

class Command(BaseCommand):
    """
    Backfill proposal codes for all proposals
    """

    help = 'Backfill proposal codes for all proposals'
    def add_arguments(self, parser):
        parser.add_argument("-y", "--year", dest="year",help='cohort year', type=str)

    def handle(self, **options):
        try:
            cohort = Cohort.objects.get(year=options.get("year"))
        except:
            sys.stderr.write(f'No cohort matching {options.get("year")}\n')
            sys.exit(0)

        # Find all submitted proposals from Cohort
        proposals = Proposal.objects.filter(cohort=cohort, status=1) # status 1 is submitted

        if not proposals:
            self.stdout.write('No proposals available')
            sys.exit(0)
        else:
            self.stdout.write(f'Found {len(proposals)} proposals. Voiding all proposal codes')
            proposals.update(code='')


        for i, proposal in enumerate(proposals):
            proposal.code = f"{cohort.year}-{i+1}"
            proposal.save()
            self.stdout.write(f'Saved {proposal.partner.name} with {proposal.code}')
