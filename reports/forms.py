from django import forms
from .models import *
from django.forms.models import inlineformset_factory


class ImpactForm(forms.ModelForm):

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


ImpactFormSet = inlineformset_factory(Report, Imprint, form=ImpactForm, extra=1, can_delete=True)
