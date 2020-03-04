import sys, csv, time, sqlite3, webbrowser, argparse
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from itertools import islice

def calculate_haversine(lat1, lon1, lat2, lon2):
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
    Apply haversine to every row in dataframe and exclude visited places
    """
    if x.Visited==False:
        distance = calculate_haversine(lat, lon, x.latitude, x.longitude)
    else:
        distance = None
    return distance

def main():

    start_time = time.perf_counter()
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
            print(f'\nProgram took: {time.perf_counter() - start_time} seconds')
            empty_list = True
            not_completed = False
        else:
            #Check 2 nearest locations distances and how many beer types they contain
            compare_min_df = haversine_df.nsmallest(2)
            first_loc_distance = int(compare_min_df.iloc[0])
            second_loc_distance = int(compare_min_df.iloc[1])
            first_loc_beer_count = int(beer_count_df.loc[compare_min_df[:1].index[0]].values)
            second_loc_beer_count = int(beer_count_df.loc[compare_min_df[1:].index[0]].values)

            #Optimize for better results/Collect more types of beer
            if optimize(first_loc_beer_count, second_loc_beer_count, first_loc_distance, second_loc_distance)==1:
                min_id = haversine_df.idxmin(skipna=True)
            else:
                min_id = int(compare_min_df[1:].index[0])

            #Update distance variables
            lat, lon = geocodes_df.loc[min_id, ['latitude', 'longitude']]
            distance_to_start = calculate_haversine(start_lat, start_lon, lat, lon)
            current_distance+=haversine_df[min_id]
            total_distance = current_distance + distance_to_start

            #If total distance does not exceed the limit, add current location to the list
            #Otherwise, finish the loop and adress variables for the results
            if total_distance < 2000:
                travel_df = travel_df.append(pd.Series([min_id, haversine_df[min_id]], index=travel_df.columns ), ignore_index=True)
                geocodes_df.loc[min_id, 'Visited']=True
            else:
                lat, lon = geocodes_df.loc[int(travel_df['brewery_id'].tail(1).values), ['latitude', 'longitude']]
                distance_to_start = calculate_haversine(start_lat, start_lon, lat, lon)
                current_distance-=haversine_df[min_id]
                total_distance = current_distance + distance_to_start
                not_completed = False

    if empty_list==False:
        #Displaying results
        display_travel_route(travel_df, distance_to_start, total_distance)
        display_beer_list(travel_df)
        print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))
        print('\nWould you like to see the travel route in Google Maps?(y/n)')
        question = input()
        if question.lower()=='y':
            export_results(travel_df)
            exit()
        else:
            exit()

def optimize(beer_count1, beer_count2, distance1, distance2):
    """
    Check if second location has more types of beer AND is not 2x further than the closest brewery
    Return '1' if shortest distance is a better choice
    Return '2' if second shortest distance is a better choice
    """
    if(beer_count2>beer_count1) and (distance2<distance1*2):
        return 2
    else:
        return 1

def display_travel_route(travel_df, distance_to_start, total_distance):
    """
    Prepare variables for travel route display
    """
    number_of_breweries = travel_df['brewery_id'].count()
    print(f'\nFound {number_of_breweries} beer factories:')
    print('-> HOME: ', start_lat, start_lon)
    for row in travel_df.index:
        br_id = int(travel_df.loc[row]['brewery_id'])
        geocodes_coord = geocodes_df.loc[br_id, 'latitude':'longitude']
        display_brewery(int(travel_df.loc[row]['brewery_id']),
                                breweries_df.loc[br_id]['name'],
                                geocodes_coord[0],
                                geocodes_coord[1],
                                int(travel_df.loc[row]['distance']))
    print('<- HOME: ', start_lat, start_lon, 'Distance:', distance_to_start, 'km.')
    print('\nTotal distance: ', (int(total_distance)), 'km.\n')

def display_brewery(brewery_id, name, lat, lon, distance):
    """
    To keep tight formating, check if brewery name isn't too long
    Display travel route id, name, latitude, longitude and distance
    """
    if len(name)>22:
            name = name[:22] + '...'
    print(f'-> [{brewery_id}] {name}: {lat} {lon} Distance: {distance} km.')


"""
TODO:
Separate displaying from display praparation
"""
def display_beer_list(travel_df):
    """
    Display a list of beer types collected on the travel route
    """
    print(f'Collected {count_beer(travel_df)} beer types:')
    for row in travel_df.index:
        br_id = int(travel_df.loc[row]['brewery_id'])
        if type(beers_df.loc[br_id]['name'])==str:
            name = beers_df.loc[br_id]['name']
            print(f'     -> {name}')
        else:
            for name in beers_df.loc[br_id]['name'].values:
                print(f'     -> {name}')

def count_beer(travel_df):
    """
    Count how many types of beer each brewery has
    """
    number_of_beers = 0
    for row in travel_df.index:
        br_id = int(travel_df.loc[row]['brewery_id'])
        beers = int(beer_count_df.loc[br_id])
        number_of_beers+=beers
    return number_of_beers

"""
TODO:
Make export_results only accept the string. The string has to be prepared beforehand.
"""
def export_results(travel_df):
    """
    Export results to google maps
    """
    web_str = 'http://www.google.com/maps/dir/'
    for row in travel_df.index:
        br_id = int(travel_df.loc[row]['brewery_id'])
        geocodes_coord = geocodes_df.loc[br_id, 'latitude':'longitude']
        web_str+=f'{geocodes_coord[0]},{geocodes_coord[1]}/'
    webbrowser.open(web_str)

if __name__ == '__main__':
    #Get coordinates from argparse
    parser = argparse.ArgumentParser(description='Enter coordinates')
    parser.add_argument('lat', type=float, help='Latitude')
    parser.add_argument('lon', type=float, help='Longitude')
    args = parser.parse_args()
    start_lat = args.lat
    start_lon = args.lon

    #Initiate db
    beers_df = pd.read_csv('Data/beers.csv', index_col=1)
    breweries_df = pd.read_csv('Data/breweries.csv', index_col=0)
    geocodes_df = pd.read_csv('Data/geocodes.csv', index_col=1)
    geocodes_df['Visited']=False
    beer_count_df = pd.Index(beers_df.index).value_counts().to_frame()

    main()
