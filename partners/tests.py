from django.test import TestCase
from django.http import HttpRequest

from .forms import BulkUploadUsers
from unittest.mock import patch
from django.contrib.auth.models import User

from partners.models import Partner
from .utils import create_portal_users, invite_users_to_proposal


# create a class which with mock the requests library.
# This class will be used to replace the requests library
# in our tests.
def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
        
        def json(self):
            return self.json_data

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

    def test_form_has_fields(self):
        form = BulkUploadUsers(user=self.bart, token='token')
        expected = ['proposalid', 'users']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)

    @patch('partners.forms.create_portal_users')
    @patch('partners.forms.invite_users_to_proposal')
    def test_upload_to_portal(self, mock_create_portal_users, mock_invite_users_to_proposal):
        mock_create_portal_users.return_value = (True, [])
        mock_invite_users_to_proposal.return_value = (True, [])
        request = HttpRequest()
        request.POST = {
            'proposalid' : 1,
            'users':'username, first name, last name, email, institution',
            }
        form = BulkUploadUsers(request.POST, user=self.bart, token='token')
        self.assertTrue(form.is_valid())
        form.upload_to_portal()
        self.assertEqual(form.users[0]['username'], 'username')