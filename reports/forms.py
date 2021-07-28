from django import forms
from django.utils import timezone
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Div, HTML
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from .models import *
from partners.models import Cohort, Partner

class ImpactForm(forms.ModelForm):
    period = forms.ChoiceField(label='Reporting Period', required=False)
    partner = forms.ChoiceField()
    demo_other = forms.CharField(label='Other Demographic', required=False)

    class Meta:
        model = Imprint
        fields = ('partner','audience','activity','size','demographic','demo_other','impact')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        try:
            self.report = kwargs.pop('report')
            self.partner = self.report.partner
        except:
            self.partner = None
            self.report = None

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        layout = Layout(
            Div(
                'period',
                'partner',
                'audience',
                'demographic',
                Field('demo_other', css_class="input"),
                css_class="column is-half"
            ),
            Div(
                'activity',
                Field('size', css_class="input"),
                'impact',
                ButtonHolder(
                    Submit('addimpact', 'Add Impact', css_class='button blue-bg white', css_id='submit_impact'),
                    css_class='buttons'
                ),
            css_class="column is-half"
        ),
        )

        self.helper.layout = layout
        self.helper.form_method = 'post'
        self.helper.form_class = 'columns'
        self.helper.form_id = 'impact_form'
        self.helper.form_action = ''

        if self.report:
            self.fields['period'].choices = [(self.report.period.id, self.report.period.year)]
            self.fields['period'].initial = self.report.period.id
            self.fields['period'].widget = forms.HiddenInput()
        else:
            dates = [(x.id, x.label) for x in Cohort.objects.all() if x.start < timezone.now() and x.end > timezone.now()]
            dates_extra = Cohort.objects.filter(active_report=True)
            dates.extend([ (p.id, p.label) for p in dates_extra])
            self.fields['period'].choices = set(dates)


        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['partner'].choices = choices
        if self.partner:
            self.fields['partner'].initial = self.partner.id
            self.fields['partner'].widget = forms.HiddenInput()

class ImpactFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'columns'
        self.template = 'reports/report_formset.html'
        self.layout = Layout(
            Div(
                'period',
                'partner',
                Field('countries', css_class="is-multiple"),
                css_class="column is-half"
            ),
            Div(
                'summary',
                'comment',
                ButtonHolder(
                    Submit('submit', 'Submit', css_class='button is-success')
                ),
            css_class="column is-half"
            ),
        )

ImpactFormSet = inlineformset_factory(Report, Imprint, form=ImpactForm, extra=0, can_delete=False)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['partner','countries','summary','comment']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                'partner',
                Field('countries', css_class="is-multiple"),
                css_class="column is-half"
            ),
            Div(
                'summary',
                'comment',
                ButtonHolder(
                    Submit('submit', 'Save &amp; Continue', css_class='button is-success')
                ),
                css_class="column is-half"),
        )
        self.helper.form_method = 'post'
        self.helper.form_class = 'columns'
        self.helper.form_action = ''

        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['partner'].choices = choices

class ReportEditForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['partner','countries','summary','comment']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
        Div(
            Div(
                'partner',
                Field('countries', css_class="is-multiple"),
                css_class="column is-half"
            ),
            Div(
                'summary',
                'comment',
            css_class="column is-half"),
        css_class="columns"),
        Div(
            Fieldset('Add Impact',
                    Formset('impacts')),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button is-success')
            ),
        css_class="container"),
        )
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['partner'].choices = choices
