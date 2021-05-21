from datetime import datetime

from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Partner, Region, ProgramType, Semester, Cohort, Proposal, Membership, Review


class ProposalAdmin(admin.ModelAdmin):
    @admin.display(description='Decision')
    def colour_status(self,obj):
        colours = {3:'C93419',2:'34C919',1:'FFC300',0:'AAAAAA'}
        return format_html(
            '<span style="color: #{}">{}</span>',
            colours.get(obj.status,'000000'),
            obj.get_status_display()
        )
    list_filter = ['status','cohort']
    list_display = ['title','submitter','colour_status','cohort']
    order_by = ['title','cohort']

class PartnerAdmin(admin.ModelAdmin):
    list_filter = ['active',]
    list_display = ['name','proposal_code','active']
    order_by = 'name'

class SemesterInline(admin.TabularInline):
    model = Semester

class CohortAdmin(admin.ModelAdmin):
    inlines = [SemesterInline,]

def trans_status(state):
    state_dict = {Review.ACCEPTED : 2,
            Review.REJECTED : 3,
            Review.QUESTIONS : 1}
    try:
        return state_dict[state]
    except KeyError:
        return 0

class ReviewAdmin(admin.ModelAdmin):
    @admin.action(description='Email verdict')
    def email_verdict(modeladmin, request, queryset):

        for obj in queryset:
            obj.email_verdict()
            obj.emailed = datetime.utcnow()
            obj.proposal.status = trans_status(obj.verdict)
            obj.proposal.save()
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
    actions = [email_verdict]

admin.site.register(Semester)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Region)
admin.site.register(ProgramType)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Membership)
admin.site.register(Review, ReviewAdmin)
