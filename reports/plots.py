import io
from collections import Counter

import pandas as pd
import plotly.express as px
from django.db.models import Count, Sum
from django.conf import settings
from django.http import HttpResponse
import squarify
import matplotlib.pyplot as plt

from .countries import REGIONS
from .models import DEMOGRAPH_CHOICES, AUDIENCE_CHOICES, ACTIVITY_CHOICES, Imprint, Report, Cohort


def get_partner_sum(year):

    choices = {'demographic': DEMOGRAPH_CHOICES,
                'audience': AUDIENCE_CHOICES,
                'activity': ACTIVITY_CHOICES}
    aggregates = {}
    totals = []

    imprints = Imprint.objects.filter(report__period__year=year, activity=7)

    for plotname in ['demographic','audience','activity']:
        count = Counter()
        for i in imprints.values_list(plotname,'size'):
            count.update({i[0]:i[1]})
        opts = {d[0]:d[1] for d in choices[plotname]}
        total = sum(count.values())
        totals.append(total)
        aggregates[plotname] = [{'name':opts[k], 'number':v,'percent':f"{v/total*100:.0f}"} for k, v in dict(count).items()]

    return aggregates, max(totals)

def get_partner_counts(reports):
    total = reports.count()
    demos = reports.annotate(count=Count('imprint__demographic')).values_list('imprint__demographic','count')
    audience = reports.annotate(count=Count('imprint__audience')).values_list('imprint__audience','count')
    activity = reports.annotate(count=Count('imprint__activity')).values_list('imprint__activity','count')
    data = [
            {'source': demos, 'choices': DEMOGRAPH_CHOICES,'id':'demographics'},
            {'source': audience, 'choices': AUDIENCE_CHOICES, 'id':'audience'},
            {'source': activity, 'choices': ACTIVITY_CHOICES, 'id':'activity'},
    ]
    return breakdown_per_partner(data, total)

def breakdown_per_partner(data, total):
    aggregates = {}
    for datum in data:
        opts = {d[0]:d[1] for d in datum['choices']}
        counts = Counter([opts[d[0]] for d in datum['source'] if d[0] != None])
        aggregates[datum['id']] = [{'name':k, 'number':v,'percent':f"{v/total*100:.0f}"} for k, v in dict(counts).items()]
    return aggregates


def cohort_countries(year):
    cohort = Cohort.objects.get(year=year)
    count = Counter()
    regions_count = Counter()
    imprints = Imprint.objects.filter(report__period=cohort).exclude(countries=None)
    icountries = [c.alpha3 for i in imprints for c in i.countries]
    reports = Report.objects.filter(period=cohort).exclude(countries=None)
    rcountries = [c.alpha3 for i in reports for c in i.countries]
    for c in [icountries, rcountries]:
        count.update(c)

    for c in reports.values_list('countries', flat=True):
        ccodes = c.split(',')
        regions = set([REGIONS[code]['region'] for code in ccodes])
        regions_count.update(regions)
    regions_list = [{'name':k,'number':v} for k,v in dict(regions_count).items()]
    return dict(count), regions_list

def countries_summary(request, year):
    """
    For `cohort` find all the countries from
    """
    count, regions = cohort_countries(year)
    # Change index from 2 letter code to Name of country
    # data = [{'code':countries.alpha3(code=k), 'pop':v} for k,v in count.items()]
    # return JsonResponse(data, safe=False)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="countries.csv"'

    writer = csv.writer(response)
    writer.writerow(['code', 'number'])
    for k,v in count.items():
        writer.writerow([k,v])

    return response

def choropleth_map(year):
    count, regions = cohort_countries(year)
    countries = pd.DataFrame([[k,v]for k,v in count.items()],columns=['code','number'])

    fig = px.choropleth(countries, locations="code",
        color="number", # lifeExp is a column of gapminder
        color_continuous_scale=px.colors.sequential.Mint)
    return fig.to_html(full_html=False, default_height=500)

def demographics_plot(request, year, plotname):
    reports = Report.objects.filter(period__year=year)
    data = get_partner_counts(reports)
    if plotname not in data.keys():
        return Http404

    sizes = [d['number'] for d in data[plotname]]
    label = [d['name'].replace(' ','\n') for d in data[plotname]]
    squarify.plot(sizes=sizes, label=label, alpha=0.6 )
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return HttpResponse(buf.read(),content_type="image/png")
