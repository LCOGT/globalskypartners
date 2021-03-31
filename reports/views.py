from .models import *
from .forms import *
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction

# import plotly.express as px
# import pandas as pd

COUNTRIES_2020 = ['Botswana',
 'Algeria',
 'Egypt',
 'Ethiopia',
 'Kenya',
 'Libya',
 'Morocco',
 'Nigeria',
 'South Africa',
 'Zambia',
 'Zimbabwe',
 'China',
 'Cyprus',
 'India',
 'Iran',
 'Israel',
 'Sri Lanka',
 'Nepal',
 'Pakistan',
 'Qatar',
 'Turkey',
 'Taiwan',
 'Bolivia',
 'Brazil',
 'Colombia',
 'Ecuador',
 'Paraguay',
 'Venezuela',
 'Canada',
 'Haiti',
 'Nicaragua',
 'United States',
 'Belgium',
 'Switzerland',
 'Czech Rep.',
 'Germany',
 'Spain',
 'France',
 'United Kingdom',
 'Poland',
 'Portugal',
 'Romania',
 'Russia',
 'Serbia',
 'Australia',
 'New Zealand']

class ReportCreate(CreateView):
    model = Report
    fields = ['partner','countries','summary','comment']
    template_name = 'reports/report_create.html'
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ReportCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['impacts'] = ImpactFormSet(self.request.POST)
        else:
            data['impacts'] = ImpactFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        impacts = context['impact']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if impacts.is_valid():
                impacts.instance = self.object
                impacts.save()
        return super(ReportCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reports:report_detail', kwargs={'pk': self.object.pk})

def audience_map(countries):
    world_path = Path(DATA_PATH) / 'custom.geo.json'
    with open(world_path) as f:
       geo_world = json.load(f)

    # Instanciating necessary lists
    found = []
    missing = []
    countries_geo = []

    # Looping over the custom GeoJSON file
    for country in geo_world['features']:

        # Country name detection
        country_name = country['properties']['name']

        # Checking if that country is in the dataset
        if country_name in countries:

            # Adding country to our "Matched/found" countries
            found.append(country_name)

            # Getting information from both GeoJSON file and dataFrame
            geometry = country['geometry']

            # Adding 'id' information for further match between map and data
            countries_geo.append({
                'type': 'Feature',
                'geometry': geometry,
                'id':country_name
            })

        # Else, adding the country to the missing countries
        else:
            missing.append(country_name)

    # Displaying metrics
    print(f'Countries found    : {len(found)}')
    print(f'Countries not found: {len(missing)}')
    geo_world_ok = {'type': 'FeatureCollection', 'features': countries_geo}

    df = pd.DataFrame({'zone':found, 'count':len(found) * [1]})

    fig = px.choropleth(
        df,
        geojson=geo_world_ok,
        locations='zone',
        color=df['count'],
        color_continuous_scale=["red"],
        coloraxis_showscale=False
    )

    fig.update(coloraxis_showscale=False)
    fig.show()
