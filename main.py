import argparse
import csv
import sqlite3
import sys
import time
import webbrowser
import pysnooper
import pandas as pd
import pytest
from math import asin, cos, radians, sin, sqrt

# Radius of earth in kilometers.
EARTH_RADIUS = 6371

# If TRUE, results will be exported to google maps
GOOGLE_MAPS_EXPORT = False

# Max distance you want to travel, in kilometers
MAX_DISTANCE = 2000


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = EARTH_RADIUS
    return int(c * r)


def apply_distance_calc(x, lat, lon):
    return calculate_distance(lat, lon, x.latitude, x.longitude)


def calculate_ratio(row):
    return (row.beer_count + 1) / (row.distance + 0.01)


def get_next_location(distances_df, km_left):
    distances_df["distance_to_home"] = distances_df.apply(
        apply_distance_calc, args=(start_lat, start_lon), axis=1
    )
    distances_df["ratio"] = distances_df.apply(calculate_ratio, axis=1)
    print(pd.Series(distances_df.query("distance < 1000").ratio.idxmax()))
    #--Cannot idxmax on empty object
    best_next_location = pd.Series(distances_df.query("distance < 1000").ratio.idxmax())
    if distances_df.distance_to_home.loc[best_next_location].values[0]>km_left:
        return pd.Series()
    else:
        return distances_df.loc[best_next_location]


def main():
    start_time = time.perf_counter()
    lat = start_lat
    lon = start_lon
    distances_df = pd.DataFrame()
    travel_df = pd.DataFrame(
        columns=[
            "brewery_id",
            "distance",
            "name",
            "latitude",
            "longitude",
            "beer_count",
            "ratio",
        ],
        data=[["HOME", 0, "", start_lat, start_lon, 0, 0]],
    )
    # print(travel_df)
    # current_distance = 0
    # total_distance = 0
    while True:

        # Apply the distance calculation formula
        distances_df = (
            geocodes_df.query("Visited == False")
            .apply(apply_distance_calc, args=(lat, lon), axis=1)
            .rename("distance")
            .to_frame()
        )
        # Join additional data to distances_df
        distances_df = distances_df.join(
            geocodes_df[["name", "latitude", "longitude", "beer_count"]],
            on="brewery_id",
            how="inner",
        )
        km_left = MAX_DISTANCE - travel_df.distance.sum() #----distance sum incorrect
        # print(km_left, travel_df.distance.sum())
        next_valid_location = get_next_location(distances_df, km_left)
        if next_valid_location.empty:
            break
        else:
            travel_df.append(next_valid_location)
            geocodes_df.loc[next_valid_location.index.values[0], "Visited"] = True
            # break
        # Check if there's at least one location that is closer than MAX_DISTANCE
        # MAX_DISTANCE is divided by 2, since you'll need to come back to starting location

        # if distances_df.min().values[0] > (MAX_DISTANCE / 2):
        #     print(
        #         f"Sorry, no breweries within {MAX_DISTANCE}km from this starting location."
        #     )
        #     print(f"\nProgram took: {time.perf_counter() - start_time} seconds")
        #     break

        # Update distance variables

        # lat, lon = geocodes_df.loc[best_brewery_id, ["latitude", "longitude"]]
        # distance_to_start = calculate_distance(start_lat, start_lon, lat, lon)
        # current_distance += distances_df.distance.loc[best_brewery_id]
        # total_distance = current_distance + distance_to_start

        # If total distance does not exceed the limit, add current location to the list
        # Otherwise, finish the loop and adress variables for the results

        # if total_distance < MAX_DISTANCE or travel_df.empty:
        #     brewery = pd.Series(
        #         [best_brewery_id, distances_df.distance[best_brewery_id]],
        #         index=travel_df.columns,
        #     )
        #     travel_df = travel_df.append(brewery, ignore_index=True)
        #     geocodes_df.loc[best_brewery_id, "Visited"] = True
        # else:
        #     lat, lon = geocodes_df.loc[
        #         travel_df.brewery_id.tail(1).values[0], ["latitude", "longitude"]
        #     ]
        #     distance_to_start = calculate_distance(start_lat, start_lon, lat, lon)
        #     current_distance -= distances_df.distance.loc[best_brewery_id]
        #     total_distance = current_distance + distance_to_start
        #     break
        # break

    # report(travel_df, distance_to_start, start_lat, start_lon, total_distance, start_time)

    if GOOGLE_MAPS_EXPORT:
        google_maps(travel_df)


def report(
    travel_df, distance_to_start, start_lat, start_lon, total_distance, start_time
):
    """
    Print out the results
    """
    if not travel_df.empty:
        travel_df = travel_df.join(
            geocodes_df[["name", "latitude", "longitude", "beer_count"]],
            on="brewery_id",
            how="inner",
        )
        print(
            generate_travel_route(
                travel_df, start_lat, start_lon, distance_to_start, total_distance,
            )
        )
        print(generate_beer_list(travel_df, beers_df))
        print(f"\nProgram took: {time.perf_counter() - start_time} seconds")


def generate_travel_route(
    travel_df, start_lat, start_lon, distance_to_start, total_distance
):
    """
    Format a detailed list of breweries visited on the travel route
    """
    s = ""
    number_of_breweries = travel_df["brewery_id"].count()
    s += f"Found {number_of_breweries} beer factories:\n"
    s += f"-> HOME: {start_lat} {start_lon}\n"
    for _, br_id, distance, name, lat, lon, _ in travel_df.itertuples():
        if len(name) > 22:
            name = name[:22] + "..."
        s += f"-> [{br_id}] {name}: {lat} {lon} Distance: {distance} km.\n"
    s += f"<- HOME: {start_lat}, {start_lon} Distance: {distance_to_start} km.\n\n"
    s += f"Total distance: {total_distance} km.\n"
    return s


def generate_beer_list(travel_df, beers_df):
    """
    Format a detailed list of beer types collected on the travel route
    """
    s = ""
    s += f"Collected {travel_df.beer_count.sum()} beer types:\n"
    for row in travel_df.itertuples():
        for name in beers_df.loc[[row.brewery_id], "name"].values:
            s += f"     -> {name}\n"
    return s


def google_maps(travel_df):
    """
    Google maps has a limitation and can only display limited amout of destinations
    """
    if travel_df.brewery_id.count() > 15:
        exit()
    else:
        google_path = construct_google_map_path(travel_df, start_lat, start_lon)
        webbrowser.open(google_path)
        exit()


def construct_google_map_path(travel_df, start_lat, start_lon):
    """
    Make a web string for google maps
    """
    web_str = "http://www.google.com/maps/dir/"
    web_str += f"{start_lat},{start_lon}/"
    for row in travel_df.itertuples():
        web_str += f"{row.latitude},{row.longitude}/"
    web_str += f"{start_lat},{start_lon}/"
    return web_str


if __name__ == "__main__":
    # Get coordinates from argparse
    parser = argparse.ArgumentParser(description="Enter coordinates")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    args = parser.parse_args()
    start_lat = args.lat
    start_lon = args.lon

    # Initiate data
    beers_df = pd.read_csv("Data/beers.csv", index_col=1)
    breweries_df = pd.read_csv("Data/breweries.csv", index_col=0)
    geocodes_df = pd.read_csv("Data/geocodes.csv", index_col=0)
    geocodes_df = geocodes_df.join(breweries_df.name)
    geocodes_df["Visited"] = False
    geocodes_df = geocodes_df.drop_duplicates(subset="brewery_id", keep="first")
    geocodes_df = geocodes_df.set_index("brewery_id")
    beer_count = beers_df.groupby(beers_df.index).size()
    beer_count.name = "beer_count"
    geocodes_df = geocodes_df.join(beer_count, how="inner")

    main()
