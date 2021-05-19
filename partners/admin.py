from datetime import datetime

from django.contrib import admin, messages

from .models import Partner, Region, ProgramType, Semester, Cohort, Proposal, Membership, Review


class ProposalAdmin(admin.ModelAdmin):
    list_filter = ['status','cohort']
    list_display = ['title','submitter','status','cohort']
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

    list_display = ['partner_name','verdict','emailed']
    actions = [email_verdict]

admin.site.register(Semester)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Region)
admin.site.register(ProgramType)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Membership)
admin.site.register(Review, ReviewAdmin)
