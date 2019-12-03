#Max travel distance 2000km

import csv
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers.
    return int(c * r)


lat1, lon1 = 51.355468, 11.100790 #Starting location for testing
beers, breweries, geocodes = 'beers.csv', 'breweries.csv', 'geocodes.csv'


#Make geocodes dictionary from csv
geo_reader = csv.reader(open(geocodes, 'r'))
geocodes_dict = {}
for row in geo_reader:
   k, v1, v2, v3, v4 = row
   geocodes_dict[v1] = [v2, v3]
del geocodes_dict['brewery_id']


#Make breweries dictionary from csv
br_reader = csv.reader(open(breweries, 'r', encoding='utf-8'))
breweries_dict = {}
for row in br_reader:
   k, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, v13 = row
   breweries_dict[k] = v1
del breweries_dict['id']


#Make beers dictionary from csv
be_reader = csv.reader(open(beers, 'r', encoding='utf-8'))
beers_dict = {}
for row in be_reader:
   k, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12 = row
   beers_dict[v1] = v2
del beers_dict['brewery_id']


for x, y in geocodes_dict.items():
    if haversine(lat1, lon1, float(y[0]), float(y[1]))<200:
        print('Brewerie: ', breweries_dict[x], '    Beer: ', beers_dict[x])
