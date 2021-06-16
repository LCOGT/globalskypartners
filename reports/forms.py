from django import forms
from .models import *
from django.forms.models import inlineformset_factory


class ImpactForm(forms.ModelForm):
    partner = forms.ChoiceField()
    size = forms.CharField(
        max_length=5,
        widget=forms.Textarea(attrs={'class': 'input'}),
    )
    demo_other = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'class': 'textarea','rows':6}),
    )
    impact = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'class': 'textarea'}),
    )

    class Meta:
        model = Imprint
        exclude = ()

    def __init__(self, *args, **kwargs):
        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['partner'].choices = choices

ImpactFormSet = inlineformset_factory(Report, Imprint, form=ImpactForm, extra=1, can_delete=True)
