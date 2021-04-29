from partners.models import Partner

def mock_lco_authenticate(request, username, password):
    return None

def mock_api_auth(url, username, password):
    return 'FAKE-TOKEN'

def mock_get_profile(token):
    params = {'first_name': 'Bart', 'last_name':'Simpson','email':'bart@simpson.com','username':'bart'}
    return params, ''

def mock_get_proposals(token, email):
    return Partner.objects.all()
