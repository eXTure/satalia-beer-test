import argparse
import csv
import sqlite3
import sys
import time
import webbrowser
from itertools import islice
from math import asin, cos, radians, sin, sqrt

import pandas as pd
import pytest

EARTH_RADIUS = 6371


def calculate_haversine(lat1, lon1, lat2, lon2):
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
    r = EARTH_RADIUS  # Radius of earth in kilometers.
    return int(c * r)


def apply_haversine(x, lat, lon):
    return calculate_haversine(lat, lon, x.latitude, x.longitude)


def main():
    start_time = time.perf_counter()
    lat = start_lat
    lon = start_lon
    haversine_df = pd.DataFrame()
    travel_df = pd.DataFrame(columns=["brewery_id", "distance"])
    current_distance = 0
    total_distance = 0
    while True:

        # Apply the haversine formula and check if there's at least one location that is closer than 2000 km
        haversine_df = geocodes_df.apply(apply_haversine, args=(lat, lon), axis=1)
        if haversine_df.min() > 2000:
            print("Sorry, no breweries within 2000km from this starting location.")
            print(f"\nProgram took: {time.perf_counter() - start_time} seconds")
            break

        # Check 2 nearest locations distances and how many beer types they contain
        haversine_df["beer_per_kmsquared"] = haversine_df.beer_count / (
            haversine_df.distance ** 2
        )
        best_brewery_id = haversine_df.ratio.idxmax()

        # Update distance variables
        lat, lon = geocodes_df.loc[best_brewery_id, ["latitude", "longitude"]]
        distance_to_start = calculate_haversine(start_lat, start_lon, lat, lon)
        current_distance += haversine_df[best_brewery_id]
        total_distance = current_distance + distance_to_start

        # If total distance does not exceed the limit, add current location to the list
        # Otherwise, finish the loop and adress variables for the results
        if total_distance < 2000:
            brewery = pd.Series(
                [best_brewery_id, haversine_df[best_brewery_id]],
                index=travel_df.columns,
            )
            travel_df = travel_df.append(brewery, ignore_index=True)
            geocodes_df.loc[best_brewery_id, "Visited"] = True
        else:
            lat, lon = geocodes_df.loc[
                int(travel_df["brewery_id"].tail(1).values), ["latitude", "longitude"]
            ]
            distance_to_start = calculate_haversine(start_lat, start_lon, lat, lon)
            current_distance -= haversine_df[best_brewery_id]
            total_distance = current_distance + distance_to_start
            break

    if len(travel_df.index) == 0:
        # Displaying results
        display_travel_route(travel_df, distance_to_start, total_distance)
        display_beer_list(travel_df)
        print("\nProgram took: %s seconds" % (time.perf_counter() - start_time))
        print("\nWould you like to see the travel route in Google Maps?(y/n)")
        question = input()
        if question.lower() == "y":
            webbrowser.open(construct_google_map_path(travel_df))
            exit()
        else:
            exit()


def display_travel_route(
    travel_df,
    distance_to_start,
    total_distance,
    start_lat,
    start_lon,
    geocodes_df,
    breweries_df,
):
    """
    Prepare variables for travel route display
    """
    s = ""
    number_of_breweries = travel_df["brewery_id"].count()
    s += f"Found {number_of_breweries} beer factories:\n"
    s += f"-> HOME: {start_lat} {start_lon}\n"
    for row in travel_df.index:
        br_id = travel_df.loc[row]["brewery_id"]
        lat, lon = geocodes_df.loc[br_id, "latitude":"longitude"]
        name = breweries_df.loc[br_id]["name"]
        distance = travel_df.loc[row]["distance"]
        if len(name) > 22:
            name = name[:22] + "..."
        s += f"-> [{br_id}] {name}: {lat} {lon} Distance: {distance} km.\n"

    s += f"<- HOME: {start_lat}, {start_lon} Distance: {distance_to_start} km.\n"
    s += f"Total distance: {total_distance} km.\n"
    return s


def display_beer_list(travel_df):
    """
    Display a list of beer types collected on the travel route
    """
    print(f"Collected {count_beer(travel_df)} beer types:")
    for row in travel_df.index:
        br_id = travel_df.loc[row]["brewery_id"]
        if type(beers_df.loc[br_id]["name"]) == str:
            name = beers_df.loc[br_id]["name"]
            print(f"     -> {name}")
        else:
            for name in beers_df.loc[br_id]["name"].values:
                print(f"     -> {name}")


def count_beer(travel_df):
    """
    Count how many types of beer each brewery has
    """
    number_of_beers = 0
    for row in travel_df.index:
        br_id = travel_df.loc[row]["brewery_id"]
        beers = beer_count_df.loc[br_id]
        number_of_beers += beers
    return number_of_beers


def construct_google_map_path(travel_df, geocodes_df):
    """
    Export results to google maps
    """
    web_str = "http://www.google.com/maps/dir/"
    for row in travel_df.index:
        br_id = travel_df.loc[row]["brewery_id"]
        lat, lon = geocodes_df.loc[br_id, "latitude":"longitude"]
        web_str += f"{lat},{lon}/"
    return web_str


if __name__ == "__main__":
    # Get coordinates from argparse
    parser = argparse.ArgumentParser(description="Enter coordinates")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    args = parser.parse_args()
    start_lat = args.lat
    start_lon = args.lon

    # Initiate db
    beers_df = pd.read_csv("Data/beers.csv", index_col=1)
    breweries_df = pd.read_csv("Data/breweries.csv", index_col=0)
    geocodes_df = pd.read_csv("Data/geocodes.csv", index_col=1)
    geocodes_df["Visited"] = False
    beer_count_df = pd.Index(beers_df.index).value_counts().to_frame()

    main()
