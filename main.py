import sys, csv, time, sqlite3, pandas, webbrowser, argparse
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

start_time = time.perf_counter()

def main(lati, longi):

    start_time = time.perf_counter()
    start_lat = lati
    start_lon = longi

    lat = start_lat
    lon = start_lon
    current_min = 0
    haversine_list = []
    travel_list = []
    travel_list_sum = 0
    distance_to_start = 0
    already_visited = []
    #print(beers_df.iat[307, 1])#[307])
    #print(beers_df['name'][307])
    while True:
        for id, lat1, lon1 in c.execute("SELECT brewery_id, latitude, longitude FROM geocodes"):
            if id not in already_visited:
                haversine_list.append([haversine(float(lat), float(lon), float(lat1), float(lon1)), id])
            else:
                continue
        current_min = optimize(haversine_list)
        #lat = get_data(1, 'latitude', 'geocodes', 'brewery_id', str(current_min[1]))[0]
        lat = geocodes_df['latitude'][current_min[1]]
        #lon = get_data(1, 'longitude', 'geocodes', 'brewery_id', str(current_min[1]))[0]
        lon = geocodes_df['longitude'][current_min[1]]
        already_visited.append(current_min[1])
        distance_to_start = haversine(float(lat), float(lon), float(start_lat), float(start_lon))

        #Add current location to the travel list
        if (travel_list_sum + current_min[0] + distance_to_start) < 2000:
            travel_list.append(current_min)
            sum = 0
            for hav, id in travel_list:
                sum+=hav
            travel_list_sum = sum
        else:
            break
        haversine_list = []

    if travel_list!=[]:
        travel_list = max_travel_distance_check(travel_list, travel_list_sum, distance_to_start, start_lat, start_lon)
        display_travel_route(travel_list, start_lat, start_lon, travel_list_sum, distance_to_start)
        display_beer_list(travel_list)
        print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))
        print('\nWould you like to see the travel route in Google Maps?(y/n)')
        question = input()
        if question.lower()=='y':
            export_results(travel_list)
            exit()
        else:
            exit()
    else:
        print('Sorry, no breweries within 2000km from this starting location.')
        print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))

def get_data(fetch, select_d, from_d, where_d, id_d):
    """Get data from sql"""
    sql_string = 'SELECT ' + str(select_d) + ' FROM ' + str(from_d) + ' WHERE ' + str(where_d) + ' = ' + str(id_d)
    c.execute(sql_string)
    if fetch==0:
        return c.fetchall()
    else:
        return c.fetchone()

def optimize(haversine_list):
    """Optimization"""
    shortest_distance_beer_list = get_data(0, 'name', 'beers', 'brewery_id', str(sorted(haversine_list)[0][1]))
    #print(beers_df['name'][sorted(haversine_list)[0][1]])
    #shortest_distance_beer_list = list(beers_df['name'][sorted(haversine_list)[0][1]])
    second_distance_beer_list = get_data(0, 'name', 'beers', 'brewery_id', str(sorted(haversine_list)[1][1]))
    #print(shortest_distance_beer_list, second_distance_beer_list)
    #second_distance_beer_list = beers_df['name'][sorted(haversine_list)[1][1]]
    if (len(second_distance_beer_list)>len(shortest_distance_beer_list)) and \
            (len(second_distance_beer_list)<len(shortest_distance_beer_list)*2) and \
            (int(sorted(haversine_list)[1][0])<int(sorted(haversine_list)[0][0])*2):
        return sorted(haversine_list)[1]
    else:
        return sorted(haversine_list)[0]


def max_travel_distance_check(travel_list, travel_list_sum, distance_to_start, start_lat, start_lon):
    """Make sure final travel list does not exceed 2000km"""
    while (travel_list_sum+distance_to_start)>2000:
        del travel_list[-1]
        #lat2 = get_data(1, 'latitude', 'geocodes', 'brewery_id', str(travel_list[-1][1]))[0]
        lat2 = geocodes_df['latitude'][travel_list[-1][1]]
        #lon2 = get_data(1, 'longitude', 'geocodes', 'brewery_id', str(travel_list[-1][1]))[0]
        lon2 = geocodes_df['longitude'][travel_list[-1][1]]
        distance_to_start = haversine(float(lat2), float(lon2), float(start_lat), float(start_lon))
    return travel_list

def display_travel_route(travel_list, start_lat, start_lon, distance_to_start, travel_list_sum):
    """Display the route"""
    print('\nFound {} beer factories:'.format(len(travel_list)))
    print('-> HOME: ', start_lat, start_lon)
    str_tmp = '-> [{0}] {1}: {2} {3} Distance: {4} km.'
    for hav, id in travel_list:
        #breweries_qr = get_data(1, 'name', 'breweries', 'id', str(id))
        breweries_qr = breweries_df.loc[id, 'name']
        #print(breweries_qr)
        #geocodes_qr = get_data(1, 'latitude, longitude', 'geocodes', 'brewery_id', str(id))
        geocodes_qr = geocodes_df.loc[id, 'latitude':'longitude']
        #print(geocodes_df.loc[id, 'latitude':'longitude'])#[id])
        #geocodes_qr = geocodes_df['latitude', 'longitude'][id]
        breweries_qr_str = str(breweries_qr[0])
        if len(breweries_qr)>22:
            breweries_qr = breweries_qr[:22] + '...'
        print(str_tmp.format(id, breweries_qr, geocodes_qr[0], geocodes_qr[1], hav))
    print('<- HOME: ', start_lat, start_lon, 'Distance:', distance_to_start, 'km.')
    print('\nTotal distance: ', (travel_list_sum+distance_to_start), 'km.\n')

def display_beer_list(travel_list):
    """Display a list of beers collected on the route"""
    print('Collected {} beer types:'.format(count_beer(travel_list)))
    for hav, id in travel_list:
        beers_qr = get_data(0, 'name', 'beers', 'brewery_id', str(id))
        try:
            if len(beers_qr)>1:
                for beer in beers_qr:
                    print('     ->', beer[0])
            else:
                print('     ->', str(beers_qr[0]).strip('()').strip("''").strip(',').strip("'"))
        except Exception as e:
            pass

def count_beer(travel_list):
    beer_count = 0
    for hav, id in travel_list:
        beers_qr = get_data(0, 'name', 'beers', 'brewery_id', str(id))
        for beer in beers_qr:
            if len(beer)>1:
                for i in beer:
                    beer_count+=1
            else:
                beer_count+=1
    return beer_count

def export_results(travel_list):
        web_str = 'http://www.google.com/maps/dir/'
        geocodes_list = []
        for hav, id in travel_list:
            geo1 = get_data(1, 'latitude', 'geocodes', 'brewery_id', str(id))[0]
            geo2 = get_data(1, 'longitude', 'geocodes', 'brewery_id', str(id))[0]
            geocodes_list.append((geo1, geo2))
        geocodes_list.append(geocodes_list[0])
        for geo in geocodes_list:
            web_str+=str(geo[0])+','+str(geo[1])+'/'
        webbrowser.open(web_str)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enter coordinates')
    parser.add_argument('lat', type=str, help='Latitude')
    parser.add_argument('lon', type=str, help='Longitude')
    args = parser.parse_args()
    conn = sqlite3.connect('beer.db')
    c = conn.cursor()
    pandas.read_csv('beers.csv').to_sql('beers', conn, if_exists='replace', index=False)
    pandas.read_csv('breweries.csv').to_sql('breweries', conn, if_exists='replace', index=False)
    pandas.read_csv('geocodes.csv').to_sql('geocodes', conn, if_exists='replace', index=False)
    beers_df = pd.read_csv('beers.csv', index_col=1)
    breweries_df = pd.read_csv('breweries.csv', index_col=0)
    geocodes_df = pd.read_csv('geocodes.csv', index_col=1)

    main(args.lat, args.lon)
