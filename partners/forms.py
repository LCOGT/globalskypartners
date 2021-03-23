from django import forms

from .models import Proposal, Partner

class ProposalForm(forms.ModelForm):
    title = forms.CharField(label="project title", required=False)
    title_options = forms.ChoiceField(label="extend existing project", required=False)
    class Meta:
        model = Proposal
        fields = ['title','title_options','people','institution','description','use','experience','size','support','help','extension','time','time_reason','comments']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'input'})
        projects = Partner.objects.filter(submitter=self.user)
        if projects:
            print(projects)
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['title_options'].choices = choices
        else:
            self.fields['title_options'].disabled = True
