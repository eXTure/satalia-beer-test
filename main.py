import csv
from math import radians, cos, sin, asin, sqrt
from itertools import islice

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

beers, breweries, geocodes = 'beers.csv', 'breweries.csv', 'geocodes.csv'

#Make geocodes dictionary from csv
geo_reader = csv.reader(open(geocodes, 'r', encoding='utf-8'))
geocodes_dict = {}
row_num = 0
for row in islice(geo_reader, 1, None):
    k, v1, v2, v3, v4 = row
    geocodes_dict[int(v1)] = [v2, v3]

#Make breweries dictionary from csv
br_reader = csv.reader(open(breweries, 'r', encoding='utf-8'))
breweries_dict = {}
for row in islice(br_reader, 1, None):
   k, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, v13 = row
   breweries_dict[int(k)] = v1

#Make beers dictionary from csv
be_reader = csv.reader(open(beers, 'r', encoding='utf-8'))
beers_dict = {}
for row in islice(be_reader, 1, None):
   k, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12 = row
   beers_dict[int(v1)] = v2

start_lat1, start_lon1 = '51.355468', '11.100790'
lat1, lon1 = '51.355468', '11.100790' #Starting location for testing
current_min = 0
haversine_list = []
travel_list = []
travel_list_sum = 0
distance_to_start = 0
while True:
    for id, geo in geocodes_dict.items():
        haversine_list.append([haversine(float(lat1), float(lon1), float(geo[0]), float(geo[1])), id])
    current_min = sorted(haversine_list)[0]
    lat1, lon1 = geocodes_dict[current_min[1]]
    del geocodes_dict[current_min[1]]
    #print(breweries_dict[current_min[1]])
    distance_to_start = haversine(float(lat1), float(lon1), float(start_lat1), float(start_lon1))
    #print('Distance to start', distance_to_start)
    #print(travel_list)
    if ((travel_list_sum+current_min[0]) + distance_to_start)< 2000:
        #print((travel_list_sum+current_min[0]) + distance_to_start)
        travel_list.append(current_min)
        for hav, id in travel_list:
            travel_list_sum+=hav
        #print('travel_list', travel_list)
        #print('travel_list_sum', travel_list_sum)
    else:
        travel_list_sum = travel_list_sum-travel_list[-1][0]
        try:
            for hav, id in travel_list:
                print('Brewerie: ', breweries_dict[id], '    Beer: ', beers_dict[id])
        except KeyError:
            print('')
        #print('travel_list_sum', travel_list_sum)
        #print('distance_to_start', distance_to_start)
        #travel_list_sum+=distance_to_start
        #print('travel_list_sum', travel_list_sum)
        travel_list[-1] = ['Start Location']
        print('travel_list', travel_list)
        print('Total distance: ', travel_list_sum, 'km.')
        break
    haversine_list = []
