import sys, csv, time, sqlite3, webbrowser, argparse
import pandas as pd
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

def apply_haversine(x, lat, lon):
    """Calculate distance based on 2 coordinates and exclude visited places"""
    if x.Visited==False:
        distance = haversine(lat, lon, x.latitude, x.longitude)
    else:
        distance = None
    return distance

start_time = time.perf_counter()

def main(lati, longi):

    start_time = time.perf_counter()
    start_lat = lati
    start_lon = longi
    lat = start_lat
    lon = start_lon
    print(lat, lon)
    haversine_df = pd.DataFrame()
    travel_df = pd.DataFrame(columns=['brewery_id'])
    current_distance = 0
    total_distance = 0
    not_completed = True

    while not_completed:

        haversine_df = geocodes_df.apply(apply_haversine, args=(lat, lon), axis=1)
        compare_min_df = haversine_df.nsmallest(2)
        first_loc_beer_count = int(beer_count_df.loc[compare_min_df[:1]].values)
        second_loc_beer_count = int(beer_count_df.loc[compare_min_df[1:]].values)

        #If second location has more types of beer AND is not futher than the closest loaction distance*2
        if(second_loc_beer_count>first_loc_beer_count) and (int(compare_min_df[1:])<(int(compare_min_df[:1]))*2):
            min_id = int(compare_min_df[1:].index[0])
        else:
            min_id = haversine_df.idxmin(skipna=True)

        lat, lon = geocodes_df.loc[min_id, ['latitude', 'longitude']]
        distance_to_start = haversine(start_lat, start_lon, lat, lon)
        current_distance+=haversine_df[min_id]
        total_distance = current_distance + distance_to_start

        if total_distance < 2000:
            travel_df = travel_df.append(pd.Series([min_id], index=travel_df.columns ), ignore_index=True)
            geocodes_df.loc[min_id, 'Visited']=True
        else:
            lat, lon = geocodes_df.loc[int(travel_df.tail(1).values), ['latitude', 'longitude']]
            distance_to_start = haversine(start_lat, start_lon, lat, lon)
            current_distance-=haversine_df[min_id]
            total_distance = current_distance + distance_to_start
            not_completed = False

    print(travel_df, total_distance)

    # if travel_list!=[]:
    #     travel_list = max_travel_distance_check(travel_list, travel_list_sum, distance_to_start, start_lat, start_lon)
    #     display_travel_route(travel_list, start_lat, start_lon, travel_list_sum, distance_to_start)
    #     display_beer_list(travel_list)
    #     print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))
    #     print('\nWould you like to see the travel route in Google Maps?(y/n)')
    #     question = input()
    #     if question.lower()=='y':
    #         export_results(travel_list)
    #         exit()
    #     else:
    #         exit()
    # else:
    #     print('Sorry, no breweries within 2000km from this starting location.')
    #     print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))

# def optimize(haversine_list):
#     """Optimization"""
#     shortest_distance_beer_list = get_data(0, 'name', 'beers', 'brewery_id', str(sorted(haversine_list)[0][1]))
#     #print(beers_df['name'][sorted(haversine_list)[0][1]])
#     #shortest_distance_beer_list = list(beers_df['name'][sorted(haversine_list)[0][1]])
#     second_distance_beer_list = get_data(0, 'name', 'beers', 'brewery_id', str(sorted(haversine_list)[1][1]))
#     #print(shortest_distance_beer_list, second_distance_beer_list)
#     #second_distance_beer_list = beers_df['name'][sorted(haversine_list)[1][1]]
#     if (len(second_distance_beer_list)>len(shortest_distance_beer_list)) and \
#             (len(second_distance_beer_list)<len(shortest_distance_beer_list)*2) and \
#             (int(sorted(haversine_list)[1][0])<int(sorted(haversine_list)[0][0])*2):
#         return sorted(haversine_list)[1]
#     else:
#         return sorted(haversine_list)[0]


# def max_travel_distance_check(travel_list, travel_list_sum, distance_to_start, start_lat, start_lon):
#     """Make sure final travel list does not exceed 2000km"""
#     while (travel_list_sum+distance_to_start)>2000:
#         del travel_list[-1]
#         lat2 = geocodes_df['latitude'][travel_list[-1][1]]
#         lon2 = geocodes_df['longitude'][travel_list[-1][1]]
#         distance_to_start = haversine(float(lat2), float(lon2), float(start_lat), float(start_lon))
#     return travel_list

# def display_travel_route(travel_list, start_lat, start_lon, distance_to_start, travel_list_sum):
#     """Display the route"""
#     print('\nFound {} beer factories:'.format(len(travel_list)))
#     print('-> HOME: ', start_lat, start_lon)
#     str_tmp = '-> [{0}] {1}: {2} {3} Distance: {4} km.'
#     for hav, id in travel_list:
#         breweries_qr = breweries_df.loc[id, 'name']
#         geocodes_qr = geocodes_df.loc[id, 'latitude':'longitude']
#         breweries_qr_str = str(breweries_qr[0])
#         if len(breweries_qr)>22:
#             breweries_qr = breweries_qr[:22] + '...'
#         print(str_tmp.format(id, breweries_qr, geocodes_qr[0], geocodes_qr[1], hav))
#     print('<- HOME: ', start_lat, start_lon, 'Distance:', distance_to_start, 'km.')
#     print('\nTotal distance: ', (travel_list_sum+distance_to_start), 'km.\n')

# def display_beer_list(travel_list):
#     """Display a list of beers collected on the route"""
#     print('Collected {} beer types:'.format(count_beer(travel_list)))
#     for hav, id in travel_list:
#         #beers_qr = get_data(0, 'name', 'beers', 'brewery_id', str(id))
#         #try:
#         #print(beers_df[id, 'name'])
#         beers_qr = beers_df.loc[[id]['name']]#.to_string()#.to_list()
#         #print(beers_qr)
#         #if len(beers_qr.index)>1:
#         #    for name in beers_qr:
#         #        print('     ->', name)
#         #else:
#         print(beers_qr)
#         #print('     ->', str(beers_qr).strip('()').strip("''").strip(',').strip("'"))
#         #except Exception as e:
#         #    pass

# def count_beer(travel_list):
#     beer_count = 0
#     for hav, id in travel_list:
#         beers_qr = get_data(0, 'name', 'beers', 'brewery_id', str(id))
#         for beer in beers_qr:
#             if len(beer)>1:
#                 for i in beer:
#                     beer_count+=1
#             else:
#                 beer_count+=1
#     return beer_count

# def export_results(travel_list):
#         web_str = 'http://www.google.com/maps/dir/'
#         geocodes_list = []
#         for hav, id in travel_list:
#             geo1 = get_data(1, 'latitude', 'geocodes', 'brewery_id', str(id))[0]
#             geo2 = get_data(1, 'longitude', 'geocodes', 'brewery_id', str(id))[0]
#             geocodes_list.append((geo1, geo2))
#         geocodes_list.append(geocodes_list[0])
#         for geo in geocodes_list:
#             web_str+=str(geo[0])+','+str(geo[1])+'/'
#         webbrowser.open(web_str)

if __name__ == '__main__':
    #Get coordinates from argparse
    parser = argparse.ArgumentParser(description='Enter coordinates')
    parser.add_argument('lat', type=float, help='Latitude')
    parser.add_argument('lon', type=float, help='Longitude')
    args = parser.parse_args()

    #Initiate db
    beers_df = pd.read_csv('beers.csv', index_col=1)
    breweries_df = pd.read_csv('breweries.csv', index_col=1)
    geocodes_df = pd.read_csv('geocodes.csv', index_col=1)
    geocodes_df['Visited']=False
    beer_count_df = pd.Index(beers_df.index).value_counts().to_frame()

    main(args.lat, args.lon)
