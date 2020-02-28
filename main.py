import sys, csv, time, sqlite3, webbrowser, argparse
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from itertools import islice

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    #Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    #Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 #Radius of earth in kilometers.
    return int(c * r)

def apply_haversine(x, lat, lon):
    """
    Calculate distance based on 2 coordinates and exclude visited places
    """
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
    haversine_df = pd.DataFrame()
    travel_df = pd.DataFrame(columns=['brewery_id', 'distance'])
    current_distance = 0
    total_distance = 0
    empty_list = False
    not_completed = True

    while not_completed:

        #Apply the haversine formula and check if there's at least one location that is closer than 2000 km
        haversine_df = geocodes_df.apply(apply_haversine, args=(lat, lon), axis=1)
        if haversine_df.min()>2000:
            print('Sorry, no breweries within 2000km from this starting location.')
            print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))
            empty_list = True
            not_completed = False
        else:
            #Check 2 nearest locations distances and how many beer types they contain
            compare_min_df = haversine_df.nsmallest(2)
            first_loc_beer_count = int(beer_count_df.loc[compare_min_df[:1]].values)
            second_loc_beer_count = int(beer_count_df.loc[compare_min_df[1:]].values)

            #Optimize for better results
            min_id = optimize(haversine_df, compare_min_df, first_loc_beer_count, second_loc_beer_count, int(compare_min_df[:1]), int(compare_min_df[1:]))

            #Update distance variables
            lat, lon = geocodes_df.loc[min_id, ['latitude', 'longitude']]
            distance_to_start = haversine(start_lat, start_lon, lat, lon)
            current_distance+=haversine_df[min_id]
            total_distance = current_distance + distance_to_start

            #If total distance does not exceed the limit, add current location to the list
            #Otherwise, finish the loop and adress variables for the results
            if total_distance < 2000:
                travel_df = travel_df.append(pd.Series([min_id, haversine_df[min_id]], index=travel_df.columns ), ignore_index=True)
                geocodes_df.loc[min_id, 'Visited']=True
            else:
                lat, lon = geocodes_df.loc[int(travel_df['brewery_id'].tail(1).values), ['latitude', 'longitude']]
                distance_to_start = haversine(start_lat, start_lon, lat, lon)
                current_distance-=haversine_df[min_id]
                total_distance = current_distance + distance_to_start
                not_completed = False

    print(travel_df, total_distance)

    if empty_list==False:
        #Displaying results
        display_travel_route(travel_df, start_lat, start_lon, distance_to_start, total_distance)
        display_beer_list(travel_df)
        print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))
        #print('\nWould you like to see the travel route in Google Maps?(y/n)')
        # question = input()
        # if question.lower()=='y':
        #     export_results(travel_list)
        #     exit()
        # else:
        #     exit()

def optimize(haversine_df, min_df, beer_count1, beer_count2, distance1, distance2):
    """
    Choose second location if it has more types of beer AND
    the place is not 2x further than the closest brewery
    """
    if(beer_count2>beer_count1) and (distance2<distance1*2):
        return int(min_df[1:].index[0])
    else:
        return haversine_df.idxmin(skipna=True)

def display_travel_route(travel_df, start_lat, start_lon, distance_to_start, total_distance):
    """
    Display every travel route id, name, latitude, longitude and distance
    """
    print('\nFound {} beer factories:'.format(travel_df['brewery_id'].count()))
    print('-> HOME: ', start_lat, start_lon)
    for row in travel_df.index:
        br_id = int(travel_df.loc[row]['brewery_id'])
        brewery_name = breweries_df.loc[br_id]['name']
        geocodes_coord = geocodes_df.loc[br_id, 'latitude':'longitude']
        distance = int(travel_df.loc[row]['distance'])
        #To keep tight formating, check if brewery name isn't too long
        if len(brewery_name)>22:
            brewery_name = brewery_name[:22] + '...'
        print(f'-> [{br_id}] {brewery_name}: {geocodes_coord[0]} {geocodes_coord[1]} Distance: {distance} km.')
    print('<- HOME: ', start_lat, start_lon, 'Distance:', distance_to_start, 'km.')
    print('\nTotal distance: ', (int(total_distance)), 'km.\n')

def display_beer_list(travel_df):
    """
    Display a list of beer types collected on the travel route
    """
    # print('Collected {} beer types:'.format(count_beer(travel_list)))
    # for hav, id in travel_list:
    #     #beers_qr = get_data(0, 'name', 'beers', 'brewery_id', str(id))
    #     #try:
    #     #print(beers_df[id, 'name'])
    #     beers_qr = beers_df.loc[[id]['name']]#.to_string()#.to_list()
    #     #print(beers_qr)
    #     #if len(beers_qr.index)>1:
    #     #    for name in beers_qr:
    #     #        print('     ->', name)
    #     #else:
    #     print(beers_qr)
    #     #print('     ->', str(beers_qr).strip('()').strip("''").strip(',').strip("'"))
    #     #except Exception as e:
    #     #    pass

def count_beer(travel_df):
    """
    Count the number of beers
    """
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

def export_results(travel_list):
    """
    Export results to google maps
    """
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
    beers_df = pd.read_csv('Data/beers.csv', index_col=1)
    breweries_df = pd.read_csv('Data/breweries.csv', index_col=0)
    geocodes_df = pd.read_csv('Data/geocodes.csv', index_col=1)
    geocodes_df['Visited']=False
    beer_count_df = pd.Index(beers_df.index).value_counts().to_frame()

    main(args.lat, args.lon)
