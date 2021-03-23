import sys
import csv
import requests
from datetime import datetime

from django.core.management.base import CommandError, BaseCommand
from django.conf import settings

from partners.models import Cohort, Partner
from reports.models import Report


class Command(BaseCommand):
    """
    Import old report spreadsheets
    """

    help = 'Import old report spreadsheets'
    def add_arguments(self, parser):
        parser.add_argument("-c", "--cohort", dest="cohort",help='reporting year/cohort', type=str)
        parser.add_argument("-p", "--proposal", dest="proposal",help='proposal code for partner', type=str)

    def handle(self, **options):
        total_users = 0
        total_timeused = {}
        try:
            cohort = Cohort.objects.get(year=options.get("cohort"))
        except:
            sys.stderr.write(f'No cohort matching {options.get("cohort")}\n')
            sys.exit(0)

        year = cohort.year
        if options.get("proposal",None):
            partners = Partner.objects.filter(proposal=options.get('proposal'))
        else:
            partners = cohort.partner_set.all()
        for partner in partners:
            pid = partner.proposal
            query_params = "proposals/{}/".format(pid)
            data = submit_portal_request(query_params)
            user_count = membership_total(partner.proposal)
            total_users += user_count

            print("# {}".format(data['title']))
            timeused, allocation = year_data(data,year)

            start = datetime(int(year), 1, 1)
            end = datetime(int(year)+1, 1, 1)

            self.stdout.write("{},{:.2f},{:.1f},{}".format(pid, timeused, allocation, user_count))

            req_total = request_stats(pid, start.isoformat(" "), end.isoformat(" "))
            total_timeused[pid] = {'timeused' : timeused,
                                    'allocation' : allocation,
                                    'requests_num' : req_total,
                                    'user_count' : user_count}

        failed = 0
        complete = 0
        total = 0
        for k,v in total_timeused.items():
            failed += v['requests_num']['failed']
            complete += v['requests_num']['complete']
            total += v['timeused']
        self.stdout.write(f"Total users {total_users}")
        self.stdout.write(f"Success rate: {failed} / {complete} => {(1-failed/complete)*100:.1f}")
        self.stdout.write(f"Time used {total:.2f}")


def submit_portal_request(query_params):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    headers = {'Authorization': 'Token {}'.format(settings.TOKEN)}
    url = "{}{}".format(settings.API_URL, query_params)
    # print('Request info on {}'.format(query_params))
    try:
        r = requests.get(url, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        print(msg)
        return False
    return r.json()

def membership_total(proposal):
    q = f"memberships/?role=CI&proposal={proposal}"
    resp = submit_portal_request(q)
    return resp['count']

def user_data(users, proposal, start, end):
    user_data = {}
    request_total = 0
    for user in users:
        query_params_complete = "requestgroups/?proposal={}&state=COMPLETED&created_after={}&created_before={}&user={}".format(proposal, start, end, user)
        query_params_pending = "requestgroups/?proposal={}&state=PENDING&created_after={}&created_before={}&user={}".format(proposal, start, end, user)
        c_resp = submit_portal_request(query_params_complete)
        p_resp = submit_portal_request(query_params_pending)
        if c_resp and p_resp:
            user_data[user] = {'complete':c_resp['count'], 'pending' : p_resp['count']}
            request_total += float(c_resp['count'])
    return user_data, request_total

def request_stats(proposal, start, end):
    request_data = {}
    query_params_complete = "requestgroups/?proposal={}&state=COMPLETED&created_after={}&created_before={}".format(proposal, start, end)
    query_params_pending = "requestgroups/?proposal={}&state=WINDOW_EXPIRED&created_after={}&created_before={}".format(proposal, start, end)
    c_resp = submit_portal_request(query_params_complete)
    p_resp = submit_portal_request(query_params_pending)
    if c_resp and p_resp:
        return {'complete':c_resp['count'], 'failed' : p_resp['count']}
    else:
        return {'complete': 0, 'failed' : 0}

def year_data(data, year=None):
    time_used = 0
    allocation = 0
    for ta in data['timeallocation_set']:
        if ta['semester'][0:4] == year:
            time_used += ta["std_time_used"]
            allocation += ta["std_allocation"]

    return time_used, allocation
