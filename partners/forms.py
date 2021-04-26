from django import forms
from django.core.exceptions import ValidationError

from .models import Proposal, Partner

class ProposalForm(forms.ModelForm):
    CHOICES = (('extend', 'Extend existing project'),('create','Create a new proposal'))
    title = forms.CharField(label="project title", required=False)
    summary = forms.CharField(max_length=600, label="summary", required=False, widget=forms.Textarea)
    title_options = forms.ChoiceField(label="extend existing project", required=False)
    new_or_old = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    class Meta:
        model = Proposal
        fields = ['people','institution','description','use','experience','size','support','help','time','time_reason','comments']


    def clean(self):
        data = super().clean()
        title = data.get("title")
        title_options = data.get("title_options")
        summary = data.get("summary")
        editing = data.get('new_or_old')

        if not title and not title_options:
            raise ValidationError("Either select existing project or enter a title")
        else:
            if title_options and editing == 'extend':
                partner = Partner.objects.get(id=title_options)
            else:
                if not summary:
                    raise ValidationError("Provide a summary of the project")
                else:
                    partner = Partner(name=title, summary=summary)
                    partner.save()

            data['partner'] = partner
            data['submitter'] = self.user
        return data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        if kwargs.get('partner', None):
            self.partner = kwargs.pop('partner')
        else:
            self.partner = None

        super().__init__(*args, **kwargs)
        if self.partner:
            if self.partner.is_pending():
                self.initial['new_or_old'] = 'create'
            else:
                self.initial['new_or_old'] = 'extend'
        self.fields['title'].widget.attrs.update({'class': 'input'})
        self.fields['summary'].widget.attrs.update({'class': 'textarea'})
        self.fields['people'].widget.attrs.update({'class': 'textarea'})
        self.fields['description'].widget.attrs.update({'class': 'textarea'})
        self.fields['use'].widget.attrs.update({'class': 'textarea'})
        self.fields['experience'].widget.attrs.update({'class': 'textarea'})
        self.fields['support'].widget.attrs.update({'class': 'textarea'})
        self.fields['help'].widget.attrs.update({'class': 'textarea'})
        self.fields['time_reason'].widget.attrs.update({'class': 'textarea'})
        self.fields['comments'].widget.attrs.update({'class': 'textarea'})

        if self.partner:
            self.initial['title_options'] = self.partner.id
            self.initial['title'] = self.partner.name
            self.initial['summary'] = self.partner.summary

        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['title_options'].choices = choices
        else:
            self.fields['title_options'].choices = [(u'', u'No projects available'),]
            self.fields['title_options'].disabled = True
