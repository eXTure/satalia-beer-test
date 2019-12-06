import csv, time
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

def main():

    start_lat = input('Please enter the latitude:')
    start_lon = input('Please enter the longitude:')
    start_time = time.perf_counter()
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

    lat = start_lat
    lon = start_lon
    current_min = 0
    haversine_list = []
    travel_list = []
    travel_list_sum = 0
    distance_to_start = 0
    already_visited = []
    while True:
        for id, geo in geocodes_dict.items():
            if id not in already_visited:
                haversine_list.append([haversine(float(lat), float(lon), float(geo[0]), float(geo[1])), id])
            else:
                continue
        current_min = sorted(haversine_list)[0]
        lat, lon = geocodes_dict[current_min[1]]
        already_visited.append(current_min[1])
        distance_to_start = haversine(float(lat), float(lon), float(start_lat), float(start_lon))
        if ((travel_list_sum+current_min[0]) + distance_to_start) < 2000:
            travel_list.append(current_min)
            sum = 0
            for hav, id in travel_list:
                sum+=hav
            travel_list_sum = sum
        else:
            travel_list_sum = travel_list_sum+distance_to_start
            break
        haversine_list = []

    #Display the result
    if travel_list!=[]:
        print('Travel results:')
        print('-> HOME: ', start_lat, start_lon)
        str_tmp = '-> [{0}] {1} {2} Distance: {3} km.'
        for hav, id in travel_list:
            print(str_tmp.format(id, breweries_dict[id], geocodes_dict[id], hav))
        print('<- HOME: ', start_lat, start_lon, 'Distance:', distance_to_start, 'km.')
        print('\nTotal distance: ', travel_list_sum, 'km.\n')
        print('Collected beer types:')
        try:
            for hav, id in travel_list:
                print('     ', beers_dict[id])
        except KeyError:
            pass
    else:
        print('Sorry, no breweries within 2000km from this starting point.')
    print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))

if __name__ == '__main__':
    main()
