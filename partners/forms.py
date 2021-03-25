from django import forms
from django.core.exceptions import ValidationError

from .models import Proposal, Partner

class ProposalForm(forms.ModelForm):
    title = forms.CharField(label="project title", required=False)
    summary = forms.CharField(max_length=300, label="summary", required=False)
    title_options = forms.ChoiceField(label="extend existing project", required=False)
    class Meta:
        model = Proposal
        fields = ['people','institution','description','use','experience','size','support','help','time','time_reason','comments']


    def clean(self):
        data = super().clean()
        title = data.get("title")
        title_options = data.get("title_options")
        summary = data.get("summary")

        if (not title and not title_options) or (title and title_options):
            raise ValidationError("Either select existing project or enter a title")
        else:
            if title:
                if not summary:
                    raise ValidationError("Provide a summary of the project")
                else:
                    partner = Partner(name=title, submitter=self.user, summary=summary)
                    partner.save()
            else:
                partner = Partner.objects.get(id=title_options)
            data['partner'] = partner
        return data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'class': 'input'})
        self.fields['summary'].widget.attrs.update({'class': 'textarea'})
        projects = Partner.objects.filter(submitter=self.user)
        if projects:
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['title_options'].choices = choices
        else:
            self.fields['title_options'].disabled = True
