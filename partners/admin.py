from django.contrib import admin

from .models import Partner, Region, ProgramType, Semester, Cohort, Proposal

class PartnerAdmin(admin.ModelAdmin):
    list_filter = ['active',]
    list_display = ['name','proposal_code','pi','active']
    order_by = 'name'

class SemesterInline(admin.TabularInline):
    model = Semester

class CohortAdmin(admin.ModelAdmin):
    inlines = [SemesterInline,]

admin.site.register(Semester)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Region)
admin.site.register(ProgramType)
admin.site.register(Cohort, CohortAdmin)
admin.site.register(Proposal)
