import sys
import io
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

from django.core.files.base import ContentFile
from django.core.management.base import CommandError, BaseCommand

from partners.models import Proposal, Cohort

class Command(BaseCommand):
    """
    Generate Zip archive of all submitted propsosal PDFs
    """

    help = 'Generate Zip archive of all submitted propsosal PDFs'
    def add_arguments(self, parser):
        parser.add_argument("-y", "--year", dest="year",help='cohort year', type=str)
        parser.add_argument("-p", "--path", dest="path",help='path to save proposals zip file', type=str, default=mkdtemp())

    def handle(self, **options):
        try:
            cohort = Cohort.objects.get(year=options.get("year"))
        except:
            sys.stderr.write(f'No cohort matching {options.get("year")}\n')
            sys.exit(0)

        path = Path(options.get("path"))

        # Find all submitted proposals from Cohort
        proposals = Proposal.objects.filter(cohort=cohort, status=1)

        if not proposals:
            self.stdout.write('No proposals available')
            sys.exit(0)

        pdfs = []
        for proposal in proposals:
            pdfs.append(proposal.save_pdf(path=path))
            self.stdout.write(f'Saved {proposal.partner.name}')

        zipfilename = f"proposals-{cohort.year}.zip"
        fileobj = io.BytesIO()
        with ZipFile(fileobj, 'w') as zippdfs:
            for pdffile in pdfs:
                zippdfs.write(pdffile, arcname=pdffile.name)

        cohort.proposalfile.delete(save=False)
        cohort.proposalfile.save(zipfilename, ContentFile(fileobj.getvalue()))
        cohort.save()
