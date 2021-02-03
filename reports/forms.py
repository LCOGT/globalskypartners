from django import forms
from .models import *
from django.forms.models import inlineformset_factory


class ReportForm(forms.ModelForm):

    class Meta:
        model = Imprint
        exclude = ()

ReportFormSet = inlineformset_factory(Report, Imprint, form=ReportForm, extra=1, can_delete=True)
