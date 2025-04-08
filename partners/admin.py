from datetime import datetime
import tempfile
import zipfile
import io
import csv

from django.contrib import admin, messages
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.utils.html import format_html
from django.shortcuts import render

from .models import Partner, Region, ProgramType, Semester, Cohort, Proposal, Membership, Review
from reports.models import Report, Imprint
from .utils import upload_science_application


class ProposalAdmin(admin.ModelAdmin):
    @admin.action(description="Port to reviews")
    def port_to_reviews(self, request, queryset):
        total = 0
        for obj in queryset:
            rev, c = Review.objects.get_or_create(proposal=obj)
            if c:
                total += 1
        messages.info(request, f"Ported {total}/{queryset.count()} proposals to reviews")

    @admin.action(description='Download CSV')
    def proposal_csv(self, request, queryset):
        fieldnames = ['code','submitter__email', 'partner__name','time']

        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="proposals.csv"'},
        )

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        for proposal in queryset.values(*fieldnames).order_by('id'):
            writer.writerow(proposal)
        return response

    @admin.action(description='Generate PDF')
    def generate_pdfs(modeladmin, request, queryset):
        for obj in queryset:
            return HttpResponse(
                obj.generate_pdf(),
                content_type='application/pdf',
                headers = {'Content-Disposition' : f'attachment; filename="gsp-{obj.code}.pdf"'}
            )

    @admin.action(description='Generate Proposal Zip')
    def zip_pdfs(self, request, queryset):
        tmp = io.BytesIO()
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
            for item in queryset:
                fileNameInZip = f'gsp-{item.code}.pdf'
                archive.writestr(fileNameInZip, item.generate_pdf())
        tmp.seek(0)
        return FileResponse(
                tmp,
                content_type="application/x-zip-compressed",
                headers={'Content-Disposition': 'attachment; filename="proposals.zip"', 'Content-Length' : tmp.tell()},
            )

    @admin.display(description='Decision')
    def colour_status(self,obj):
        colours = {3:'C93419',2:'34C919',1:'FFC300',0:'AAAAAA'}
        return format_html(
            '<span style="color: #{}">{}</span>',
            colours.get(obj.status,'000000'),
            obj.get_status_display()
        )
    

    @admin.display(description='Sync with Observing Portal')
    def push_to_portal(self, request, queryset):
        if 'apply' in request.POST:
            success = upload_science_application(queryset)
            self.message_user(request,
                             f"Synced {len(success)} / {queryset.count()} partners with Observation Portal")
            return HttpResponseRedirect(request.get_full_path())
                        
        return render(request,
                      'admin/order_intermediate.html',
                      context={'partners':queryset})

    list_filter = ['status','cohort']
    list_display = ['title','submitter','time','colour_status','cohort']
    order_by = ['title','cohort']
    actions = ['generate_pdfs','zip_pdfs','proposal_csv','port_to_reviews','push_to_portal']
    

class ProposalInline(admin.TabularInline):
    model = Proposal
    fields = ['cohort','submitter', 'people', 'institution']

class PartnerAdmin(admin.ModelAdmin):
    list_filter = ['active','cohorts']
    list_display = ['name','proposal_code','cohort_list','active']
    order_by = 'name'
    inlines = [ProposalInline,]

    @admin.display(description='Cohorts')
    def cohort_list(self, obj):
        return [c.year for c in obj.cohorts.all()]

class SemesterInline(admin.TabularInline):
    model = Semester

class CohortAdmin(admin.ModelAdmin):

    @admin.display(
        boolean=True,
        description='Active Call?',
    )
    def is_active_call(self, obj):
        return obj.active_call

    @admin.display(
        boolean=True,
        description='Final Report?',
    )
    def is_active_report(self, obj):
        return obj.active_report

    inlines = [SemesterInline,]
    list_display = ['year','is_active_call','is_active_report']

def trans_status(state):
    state_dict = {Review.ACCEPTED : 2,
            Review.REJECTED : 3,
            Review.QUESTIONS : 1}
    try:
        return state_dict[state]
    except KeyError:
        return 0

class ReviewAdmin(admin.ModelAdmin):
    @admin.action(description='Sync verdict')
    def sync_verdict(self, request, queryset):
        for obj in queryset:
            obj.proposal.status = trans_status(obj.verdict)
            obj.proposal.save()
        messages.info(request, f'Synced verdict for {queryset.count()} proposal(s)')


    @admin.action(description='Email verdict')
    def email_verdict(self, request, queryset):
        for obj in queryset:
            obj.email_verdict()
            obj.emailed = datetime.utcnow()
            obj.save()
        messages.info(request, f'Emailed verdict for {queryset.count()} proposal(s)')

    @admin.display()
    def partner_name(self, obj):
        return obj.proposal.partner.name

    @admin.display()
    def cohort(self, obj):
        return obj.proposal.cohort

    @admin.display(description='Decision')
    def colour_verdict(self,obj):
        colours = {0:'C93419',1:'34C919',2:'FFC300'}
        return format_html(
            '<span style="color: #{}">{}</span>',
            colours.get(obj.verdict,'000000'),
            obj.get_verdict_display()
        )

    list_display = ['partner_name','cohort','emailed','colour_verdict']
    list_filter = ['proposal__cohort', 'verdict']
    actions = ['email_verdict', 'sync_verdict']

class ReportInline(admin.TabularInline):
    model = Imprint
    fields = ['size','demographic', 'audience','activity', 'countries']

class ReportAdmin(admin.ModelAdmin):
    list_display = ['partner','period','status']
    list_filter = ['period','status']
    ordering = ['-period','partner']
    inlines = [ReportInline,]

class MembershipAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    ordering = ['user','partner']

class ImprintAdmin(admin.ModelAdmin):
    @admin.display()
    def partner(self, obj):
        return obj.report.partner.name
    @admin.display()
    def year(self, obj):
        return obj.report.period.year

    list_filter = ['demographic','activity','audience']
    list_display = ['partner','year', 'size','demographic','audience','activity']

admin.site.site_header = 'Global Sky Partner admin'

admin.site.register(Semester)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Region)
admin.site.register(ProgramType)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Imprint, ImprintAdmin)
