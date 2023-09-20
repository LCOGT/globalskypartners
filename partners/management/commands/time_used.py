import sys
import csv
import requests
from datetime import datetime
from collections import Counter

from django.db.models import Min, Max
from django.core.management.base import CommandError, BaseCommand
from django.conf import settings

from partners.models import Cohort, Partner
from reports.models import Report


class Command(BaseCommand):
    """
    Time used by partners
    """

    help = 'Time used by partners'
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

        proposal_codes = partners.values_list('proposal_code',flat=True)
        semesters = cohort.semester_set.all().values_list('code',flat=True)

        totals = get_all_proposal_times(proposal_codes, semesters)
        for partner in partners:

            user_count = membership_total(partner.proposal_code)
            total_users += user_count

            start = cohort.semester_set.aggregate(Min('start'))['start__min']
            end = cohort.semester_set.aggregate(Max('end'))['end__max']

            print(".", end =' ', flush = True)

            req_total = request_stats(partner.proposal_code, start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S"))
            total_timeused[partner.proposal_code] = {'requests_num' : req_total,
                                    'user_count' : user_count}
        self.stdout.write("\n")
        failed = 0
        complete = 0
        for k,v in total_timeused.items():
            failed += v['requests_num']['failed']
            complete += v['requests_num']['complete']
        self.stdout.write(f"Total users {total_users}")
        self.stdout.write(f"Success rate: {failed} / {complete} => {(1-failed/complete)*100:.1f}")
        self.stdout.write(f"Total Hours: {totals['total']:.2f} / {totals['used']:.2f}")


def submit_portal_request(query_params):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    headers = {'Authorization': 'Token {}'.format(settings.TOKEN)}
    url = "{}{}".format(settings.PORTAL_API_URL, query_params)

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

def get_all_proposal_times(proposal_codes, semesters):
    query_params = 'proposals/?tag=LCOEPO&limit=200'
    resp = submit_portal_request(query_params)

    totals = Counter()
    proposal_num = 0
    for proposal in resp['results']:
        if proposal['id'] in proposal_codes:
            proposal_num += 1
            # print(f"{proposal['title']} - {proposal['id']}")
            for timeset in proposal['timeallocation_set']:
                if timeset['semester'] in semesters and '0M4-SCICAM-SBIG' in timeset['instrument_types']:
                    # print(f"{timeset['std_time_used']:.2f} - {timeset['semester']}")
                    totals.update(total= timeset['std_allocation'])
                    totals.update(total= timeset['rr_allocation'])
                    totals.update(total= timeset['tc_allocation'])
                    totals.update(used = timeset['std_time_used'])
                    totals.update(used = timeset['rr_time_used'])
                    totals.update(used = timeset['tc_time_used'])
    # print(f"Number of proposals {len(proposal_codes)} vs {proposal_num}")
    return dict(totals)
