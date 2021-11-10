import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import io
from collections import Counter
from pathlib import Path

from django.db.models import Count
from django.conf import settings
from django.http import HttpResponse

from .countries import REGIONS
from .models import DEMOGRAPH_CHOICES, AUDIENCE_CHOICES, ACTIVITY_CHOICES, Imprint, Report, Cohort


def get_partner_counts(reports, total):
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
    imprints = Imprint.objects.filter(report__period=cohort).exclude(countries=None).values_list('countries', flat=True)
    reports = Report.objects.filter(period=cohort).exclude(countries=None).values_list('countries', flat=True)
    for c in [imprints, reports]:
        c_list = ",".join(c).split(',')
        count.update(c_list)
    for c in reports:
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

def choropleth_map(request, year):
    count, regions = cohort_countries(year)
    filename = Path(settings.STATICFILES_DIRS[0]) / "js" / "world.geo.json"
    df = gpd.read_file(filename)
    c_data = pd.DataFrame.from_dict({'countries':dict(count).keys(),'number':dict(count).values()})
    merged = df.merge(c_data, how='left', left_on="id", right_on="countries")
    final = merged.replace(np.nan,0)

    fig, ax = plt.subplots(1, figsize=(25, 10))
    ax.axis('off')
    ax.set_title('# partners per country', fontdict={'fontsize': '25', 'fontweight' : '3'})
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=1, vmax=37))
    fig.colorbar(sm, orientation="horizontal", fraction=0.036, pad=0.1, aspect = 30)
    final.plot(column='number', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8', norm=plt.Normalize(vmin=1, vmax=37))

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf.read(),content_type="image/png")

def demographics_plot(request,):
    breakdown_per_partner
    sizes=[50, 25, 12, 6]
    label=["50", "25", "12", "6"]
    squarify.plot(sizes=sizes, label=label, alpha=0.6 )
    plt.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf.read(),content_type="image/png")
