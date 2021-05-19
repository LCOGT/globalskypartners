from pathlib import Path

from django.core.management.base import CommandError, BaseCommand

from partners.models import Proposal, Cohort

class Command(BaseCommand):
    """
    Generate Zip archive of all submitted propsosal PDFs
    """

    help = 'Generate Zip archive of all submitted propsosal PDFs'
    def add_arguments(self, parser):
        parser.add_argument("-c", "--code", dest="code",help='cohort code', type=str)
        parser.add_argument("-p", "--path", dest="path",help='path to save proposals zip file', type=str, default='/tmp/')

    def handle(self, **options):
        try:
            cohort = Cohort.objects.get(year=options.get("cohort"))
        except:
            sys.stderr.write(f'No cohort matching {options.get("cohort")}\n')
            sys.exit(0)
        proposals = Proposal.objects.filter(cohort=cohort)
        path = Path(options.get("path"))
        if not proposals:
            self.stdout.write('No proposals available')
        for proposal in proposals:
            proposal.save_pdf(path=path)
            self.stdout.write(f'Saved {proposal.partner.name}')
