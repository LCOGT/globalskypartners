from django import forms
from django.utils import timezone
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from .models import *
from partners.models import Cohort, Partner

class ImpactForm(forms.ModelForm):
    partner = forms.ChoiceField()
    demo_other = forms.CharField(label='Other Demographic', required=False)

    class Meta:
        model = Imprint
        fields = ('partner','audience','activity','size','demographic','demo_other','impact')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'first arg is the legend of the fieldset',
                'partner',
                'audience',
                'activity',
                Field('size', css_class="input"),
                'demographic',
                Field('demo_other', css_class="input"),
                'impact'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button primary')
            )
        )
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['partner'].choices = choices


ImpactFormSet = inlineformset_factory(Report, Imprint, form=ImpactForm, extra=1, can_delete=True)
