from django.test import TestCase

from .forms import BulkUploadUsers
from unittest.mock import patch
from django.contrib.auth.models import User

from partners.models import Partner


# Create a test definition to test the BulkUploadUsers form
# The is initialised with a user and a token
# The must have a proposalid and data field
# The upload_to_portal method must be mocked to return a success

class BulkUploadUsersTest(TestCase):
    def setUp(self):
        self.username = 'bart'
        self.password = 'simpson'
        self.email = 'bart@simpson.org'
        self.bart = User.objects.create_user(username=self.username, email=self.email)
        self.bart.set_password(self.password)
        self.bart.first_name= 'Bart'
        self.bart.last_name = 'Simpson'
        self.bart.is_active=1
        self.bart.save()
        params = {
                 'name': 'AstroAwesome',
                 'proposal_code': 'LCOEPO-001',
                 'summary': 'AstroAwesome is awesome',
                 'active': True
                }
        self.partner, created = Partner.objects.get_or_create(**params)
        self.partner.pi.add(self.bart)
        self.partner.save()
        self.form = BulkUploadUsers(user=self.bart, token='token')

    def test_form_has_fields(self):
        form = self.form
        expected = ['proposalid', 'data']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)

    @patch('partners.forms.create_portal_users')
    def test_upload_to_portal(self, mock_create_portal_users):
        mock_create_portal_users.return_value = (True, [])
        data =  {'data':'username, first name, last name, email, institution', 'proposalid' : 'LCOEPO-001'}
        form = BulkUploadUsers(data=data, user=self.bart, token='token')
        form.is_valid()
        print(form.cleaned_data)
        form.upload_to_portal()



