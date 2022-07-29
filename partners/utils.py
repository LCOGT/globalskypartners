import functools
import requests
import logging

from django.conf import settings
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import CONTENT_TYPE_PNG, WeasyTemplateResponse

from partners.models import Proposal

logger = logging.getLogger(__name__)


def filter_existing_users(old_users, users):
    keys = [int(i) for i in old_users.keys()]
    newusers = []
    for k, user in enumerate(users):
        if k not in keys:
            newusers.append(user)
    return newusers

def parse_api_error(msg, users):
    errors = []
    for k, vals in msg.items():
        if 'username' in vals.keys() and 'email' not in vals.keys():
            error = ",".join(vals['username'])
            if "already exists" in error:
                errors.append(ValidationError(mark_safe(f"<strong>Fix and resubmit</strong>: {users[int(k)]['username']} registered for a different email.<br/>")))
        elif 'username' not in vals.keys() and 'email' in vals.keys():
            error = ", ".join(vals['email'])
            if "already exists" in error:
                errors.append(ValidationError(mark_safe(f"<strong>Fix and resubmit</strong>: {users[int(k)]['email']} registered for a different username<br/>")))
        elif 'username' in vals.keys() and 'email' in vals.keys():
            for field, err in vals.items():
                error_text = ','.join(err)
            if "already exists" in error_text:
                txt = f"<strong>{users[int(k)]['email']}</strong> already exists. Attempting to add to proposal.<br/>"
                errors.append(ValidationError(mark_safe(txt)))
        else:
            txt = ""
            for k, vals in msg.items():
                txt += f"User <strong>{users[int(k)]['username']}</strong> has these problems:<ul>"
                for field, err in vals.items():
                    txt += f"<li>{field} - {','.join(err)}</li>"
                txt +="</ul>"
            if txt:
                errors.append(ValidationError(mark_safe(txt)))

    if errors:
        raise ValidationError(errors)
    return

def user_submission_format(users):
    data = []
    for user in users:
        datum = {
            'email' : user[3],
            'institution' : user[4],
            'first_name' : user[1],
            'last_name' : user[2],
            'username'  : user[0],
            'password'  : User.objects.make_random_password(length=6),
            'title'     : "Mx"
        }
        data.append(datum)
    return data

def create_portal_users(users, token):
    '''
    Send the user data and the authentication token to the Portal API
    '''
    headers = {'Authorization': 'Token {}'.format(token)}

    url = "https://observe.lco.global/api/users-bulk/"
    logging.debug('Submitting to portal')
    try:
        r = requests.post(url, json={'users':users}, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logging.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logging.debug('Uploaded users')
        return True, [req['id'] for req in r.json()['requests']]
    else:
        logging.error("Could not send request: {}".format(r.content))
        return False, r.json()

def invite_users_to_proposal(emails, proposal_code, token):
    '''
    Send the user data and the authentication token to the Portal API
    '''
    headers = {'Authorization': 'Token {}'.format(token)}

    url = f"https://observe.lco.global/api/proposals/{proposal_code}/invite/"
    logging.debug('Invite users to proposal')
    try:
        r = requests.post(url, json={'emails': emails}, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logging.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logging.debug('Uploaded users')
        return True, r.json()
    else:
        logging.error("Could not send request: {}".format(r.content))
        return False, r.json()

class MyModelView(DetailView):
    # vanilla Django DetailView
    model = Proposal
    template_name = 'partners/proposal_print.html'

class CustomWeasyTemplateResponse(WeasyTemplateResponse):
    # customized response class to change the default URL fetcher
    def get_url_fetcher(self):
        # disable host and certificate check
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return functools.partial(django_url_fetcher, ssl_context=context)

class MyModelPrintView(WeasyTemplateResponseMixin, MyModelView):
    # output of MyModelView rendered as PDF with hardcoded CSS
    pdf_stylesheets = [
        settings.STATIC_ROOT + 'css/app.css',
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = False
    # custom response class to configure url-fetcher
    response_class = CustomWeasyTemplateResponse

class MyModelDownloadView(WeasyTemplateResponseMixin, MyModelView):
    # suggested filename (is required for attachment/download!)
    pdf_filename = 'foo.pdf'

class MyModelImageView(WeasyTemplateResponseMixin, MyModelView):
    # generate a PNG image instead
    content_type = CONTENT_TYPE_PNG

    # dynamically generate filename
    def get_pdf_filename(self):
        return 'foo-{at}.pdf'.format(
            at=timezone.now().strftime('%Y%m%d-%H%M'),
        )

def upload_science_application(queryset):
    return

def sciapplication_payload(queryset):
    data = []
    for obj in queryset:
        datum = {
            "title": obj.partner.name,
            "abstract": obj.description,
            "status": "string",
            "tac_rank": "",
            "call_id": obj.cohort.call_id,
            "pi": obj.submitter.email,
            "pi_first_name": obj.submitter.first_name,
            "pi_last_name": obj.submitter.last_name,
            "timerequest_set": [
                {"semester": "string",
                "std_time": 2147483647,
                "rr_time": 2147483647,
                "tc_time": 2147483647,
                "instrument_types": [
                0
                ]}
            ]
        }
    return
