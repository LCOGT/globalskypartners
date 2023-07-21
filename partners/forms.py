from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import Proposal, Partner
from .utils import create_portal_users, user_submission_format, invite_users_to_proposal, parse_api_error, filter_existing_users

import csv

class BulkUploadUsers(forms.Form):
    proposalid = forms.ChoiceField(label="Proposal")
    users = forms.CharField(label="List of users", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.token = kwargs.pop('token')
        super().__init__(*args, **kwargs)
        # This is required for create mode when there are no existing.

        choices = Partner.objects.filter(pi=self.user, active=True)
        self.fields['proposalid'] = forms.ModelChoiceField(queryset=choices)
        self.fields['users'].widget.attrs.update({'class': 'textarea'})
        self.fields['proposalid'].widget.attrs.update({'class': 'select'})

    def upload_to_portal(self):
        errors = []
        users = user_submission_format(self.cleaned_data['users'])
        self.users = users
        try:
            proposal_code = self.cleaned_data['proposalid'].proposal_code
        except Partner.DoesNotExist:
             raise ValidationError(f"Proposal ID {self.cleaned_data['proposalid']} does not exist")

        success, msg = create_portal_users(users, self.token)
        if not success:
            users_created = filter_existing_users(msg['users'], users)
            self.users = users_created
            error = parse_api_error(msg['users'], users)
            errors.append(ValidationError(mark_safe(error)))

        emails = [r['email'] for r in users]
        success, msg = invite_users_to_proposal(emails, proposal_code, self.token)
        if not success:
            invite_error = ", ".join(msg['emails'])
            errors.append(ValidationError(mark_safe(invite_error)))

        if errors:
            raise ValidationError(errors)
        return

    def clean_users(self):
        data = self.cleaned_data['users']
        user_data = []
        for row in data.split('\n'):
            user = [r.strip() for r in row.split(',')]
            if len(user) != 5:
                raise ValidationError(f"Problem with {user[0]}. Each row must have 5 fields, separated by commas; username, first name, last name, email, institution")
            user_data.append(user)
        return user_data
    
class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name','summary']
        help_texts = {
            'summary': 'Max 600 chars',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'input'})
        self.fields['summary'].widget.attrs.update({'class': 'textarea','maxlength':'600'})

class ProposalForm(forms.ModelForm):
    CHOICES = (('extend', 'Extend existing project'),('create','Create a new proposal'))
    title = forms.CharField(label="project title", required=False)
    summary = forms.CharField(max_length=600, label="summary", required=False, widget=forms.Textarea, help_text='Max 600 chars')
    title_options = forms.ChoiceField(label="extend existing project", required=False)
    new_partner_id = forms.CharField(required=False)
    new_or_old = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    class Meta:
        model = Proposal
        fields = ['people','institution','description','use','experience','size','support','help','time','time_reason','comments']


    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        title_options = cleaned_data.get("title_options")
        new_partner_id = cleaned_data.get('new_partner_id')
        summary = cleaned_data.get("summary")
        editing = cleaned_data.get('new_or_old')
        if not title and not title_options:
            raise ValidationError("Either select existing project or enter a title")
        else:
            if title_options or new_partner_id:
                partner_id = title_options if not new_partner_id else new_partner_id
                partner = Partner.objects.get(id=partner_id)
            else:
                if not summary:
                    raise ValidationError("Provide a summary of the project")
                else:
                    partner = Partner(name=title, summary=summary)
                    partner.save()
            cleaned_data['partner'] = partner
            cleaned_data['submitter'] = self.user
        cleaned_data['title_options'] = ''
        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        if kwargs.get('partner', None):
            self.partner = kwargs.pop('partner')
        else:
            self.partner = None

        super().__init__(*args, **kwargs)
        # This is required for create mode when there are no existing.
        self.fields['new_partner_id'].widget = forms.HiddenInput()
        self.fields['new_partner_id'].label = ''

        self.initial['new_or_old'] = 'create'
        if self.partner and not self.partner.is_pending():
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

        if projects := Partner.objects.filter(pi=self.user):
            choices = [(u'', u'-- Select Project --'),]
            choices.extend([ (p.id, p.name) for p in projects])
            self.fields['title_options'].choices = choices
        else:
            # self.fields['title_options'].label = 'No projects available'
            self.fields['title_options'].widget = forms.HiddenInput()
            self.fields['new_or_old'].widget = forms.HiddenInput()

        if self.partner:
            self.initial['title_options'] = self.partner.id
            self.initial['title'] = self.partner.name
            self.initial['summary'] = self.partner.summary

        if self.partner and self.partner.is_pending():
            self.initial['title_options'] = ''
            self.initial['new_partner_id'] = self.partner.id
