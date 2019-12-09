import os
os.system('pip install -r requirements.txt')
import csv, time, sqlite3, pandas
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

    conn = sqlite3.connect('beer.db')
    c = conn.cursor()
    pandas.read_csv('beers.csv').to_sql('beers', conn, if_exists='replace', index=False)
    pandas.read_csv('breweries.csv').to_sql('breweries', conn, if_exists='replace', index=False)
    pandas.read_csv('geocodes.csv').to_sql('geocodes', conn, if_exists='replace', index=False)

    lat = start_lat
    lon = start_lon
    current_min = 0
    haversine_list = []
    travel_list = []
    travel_list_sum = 0
    distance_to_start = 0
    already_visited = []
    while True:
        for id, lat1, lon1 in c.execute("SELECT brewery_id, latitude, longitude FROM geocodes"):
            if id not in already_visited:
                haversine_list.append([haversine(float(lat), float(lon), float(lat1), float(lon1)), id])
            else:
                continue

        current_min = sorted(haversine_list)[0]
        c.execute("SELECT latitude FROM geocodes WHERE brewery_id=?", (str(current_min[1]), ))
        lat = c.fetchone()[0]
        c.execute("SELECT longitude FROM geocodes WHERE brewery_id=?", (str(current_min[1]), ))
        lon = c.fetchone()[0]
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

        print('\nFound {} beer factories:'.format(len(travel_list)))
        print('-> HOME: ', start_lat, start_lon)
        str_tmp = '-> [{0}] {1}: {2} {3} Distance: {4} km.'
        for hav, id in travel_list:
            c.execute("SELECT name FROM breweries WHERE id=?", (id, ))
            breweries_qr = c.fetchone()
            c.execute("SELECT latitude, longitude FROM geocodes WHERE brewery_id=?", (id, ))
            geocodes_qr = c.fetchone()
            print(str_tmp.format(id, breweries_qr[0], geocodes_qr[0], geocodes_qr[1], hav))
        print('<- HOME: ', start_lat, start_lon, 'Distance:', distance_to_start, 'km.')
        print('\nTotal distance: ', travel_list_sum, 'km.\n')
        beer_count = 0
        for hav, id in travel_list:
            c.execute("SELECT name FROM beers WHERE brewery_id=?", (id, ))
            beers_qr = c.fetchall()
            for beer in beers_qr:
                if len(beer)>1:
                    for i in beer:
                        beer_count+=1
                else:
                    beer_count+=1
        print('Collected {} beer types:'.format(beer_count))
        for hav, id in travel_list:
            c.execute("SELECT name FROM beers WHERE brewery_id=?", (id, ))
            beers_qr = c.fetchall()
            try:
                if len(beers_qr)>1:
                    for beer in beers_qr:
                        print('     ->', beer[0])
                else:
                    print('     ->', str(beers_qr[0]).strip('()').strip("''").strip(',').strip("'"))
            except Exception as e:
                print('')
    else:
        print('Sorry, no breweries within 2000km from this starting location.')
    print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))

if __name__ == '__main__':
    main()
