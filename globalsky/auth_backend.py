from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate as dj_authenticate
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
import requests
import logging
import itertools

from django.contrib.auth.models import User

from partners.models import Partner, Membership

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class PortalBackend(object):
    """
    Authenticate against the Observing portal API.
    """

    def authenticate(self, request, username=None, password=None):
        return lco_authenticate(request, username, password)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def lco_authenticate(request, username, password):
    token = api_auth(settings.PORTAL_TOKEN_URL, username, password)
    if not token:
        messages.error(request, mark_safe("Please check your login details or <a href='https://observe.lco.global/accounts/register/'>register</a> for LCO Observation Portal account"))
        return None
    profile, msg = get_profile(token)
    username = profile['username']
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # Create a new user. There's no need to set a password
        # because Valhalla auth will always be used.
        user = User(username=username)
    user.email = profile['email']
    user.first_name = profile['first_name']
    user.last_name = profile['last_name']
    user.save()

    if proposals := get_proposals(token, username):
        for partner in proposals:
            new, obj = Membership.objects.get_or_create(user=user, partner=partner)
        # Finally add these tokens as session variables
    request.session['token'] = token

    return user


def api_auth(url, username, password):
    '''
    Request authentication cookie from the Scheduler API
    '''
    try:
        r= requests.post(url,data = {
            'username': username,
            'password': password
            }, timeout=20.0);
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        return False
    except requests.exceptions.ConnectionError:
        msg = "Trouble with internet"
        logger.error(msg)
        return False

    if r.status_code in [200,201]:
        logger.debug('Login successful for {}'.format(username))
        return r.json()['token']
    else:
        logger.error("Could not login {}: {}".format(username, r.json()['non_field_errors']))
        return False

def parse_api_response(url, token):
    token = {'Authorization': 'Token {}'.format(token)}
    try:
        r = requests.get(url, headers=token, timeout=20.0);
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        return False, _("We are currently having problems. Please bear with us")

    if r.status_code in [200,201]:
        logger.debug('Proposal lookup successful')
        return r.json(), False
    else:
        logger.error("Could not get profile {}".format(r.content))
        return False, _("Please check your login details or <a href='https://observe.lco.global/accounts/register/'>register</a> for LCO Observation Portal account")


def get_proposals(token, email):
    url = settings.PROPOSALS_URL
    results, msg = parse_api_response(url, token)
    proposals = check_proposal_membership(results['results'], email)
    return proposals

def get_profile(token):
    url = settings.PROFILE_URL
    results, msg = parse_api_response(url, token)
    return results, msg

def check_proposal_membership(proposals, email):
    # Check user has a proposal we authorize
    pis = [[proposal['id'] for pi in proposal['pis'] if pi['email'] == email] for proposal in proposals ]
    my_pis = list(itertools.chain(*pis))
    my_proposals = Partner.objects.filter(proposal_code__in=my_pis)
    if my_proposals:
        return my_proposals
    else:
        return False
