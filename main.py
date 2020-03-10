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


def main():
    start_time = time.perf_counter()
    lat = start_lat
    lon = start_lon
    distances_df = pd.DataFrame()
    travel_df = pd.DataFrame(columns=["brewery_id", "distance"])
    current_distance = 0
    total_distance = 0
    while True:

        # Apply the distance calculation formula
        distances_df = (
            geocodes_df.query("Visited == False")
            .apply(apply_distance_calc, args=(lat, lon), axis=1)
            .rename("distances")
            .to_frame()
        )

        # Check if there's at least one location that is closer than MAX_DISTANCE
        # MAX_DISTANCE is divided by 2, since you'll need to come back to starting location
        if distances_df.min().values[0] > (MAX_DISTANCE / 2):
            print(
                f"Sorry, no breweries within {MAX_DISTANCE}km from this starting location."
            )
            print(f"\nProgram took: {time.perf_counter() - start_time} seconds")
            break

        # Count the ratio to identify best next brewery to visit
        distances_df = pd.merge(
            distances_df,
            geocodes_df.beer_count,
            left_index=True,
            right_index=True,
            how="inner",
        )
        distances_df["ratio"] = distances_df.apply(
            lambda row: (row.beer_count + 1) / (row.distances + 0.01), axis=1
        )
        best_brewery_id = distances_df.query("distances < 1000").ratio.idxmax()

        # Update distance variables
        lat, lon = geocodes_df.loc[best_brewery_id, ["latitude", "longitude"]]
        distance_to_start = calculate_distance(start_lat, start_lon, lat, lon)
        current_distance += distances_df.distances.loc[best_brewery_id]
        total_distance = current_distance + distance_to_start

        # If total distance does not exceed the limit, add current location to the list
        # Otherwise, finish the loop and adress variables for the results
        if total_distance < MAX_DISTANCE or travel_df.empty:
            brewery = pd.Series(
                [best_brewery_id, distances_df.distances[best_brewery_id]],
                index=travel_df.columns,
            )
            travel_df = travel_df.append(brewery, ignore_index=True)
            geocodes_df.loc[best_brewery_id, "Visited"] = True
        else:
            lat, lon = geocodes_df.loc[
                travel_df.brewery_id.tail(1).values[0], ["latitude", "longitude"]
            ]
            distance_to_start = calculate_distance(start_lat, start_lon, lat, lon)
            current_distance -= distances_df.distances.loc[best_brewery_id]
            total_distance = current_distance + distance_to_start
            break

    if not travel_df.empty:
        # Print out the results
        print(
            generate_travel_route(
                travel_df,
                geocodes_df,
                start_lat,
                start_lon,
                distance_to_start,
                total_distance,
            )
        )
        print(generate_beer_list(travel_df, beers_df))
        print(f"\nProgram took: {time.perf_counter() - start_time} seconds")

        # Google maps has a limitation and can only display limited amout of destinations
        number_of_breweries = travel_df["brewery_id"].count()
        if number_of_breweries > 15:
            exit()
        else:
            print("\nWould you like to see the travel route in Google Maps?(y/n)")
            question = input()
            if question.lower() == "y":
                webbrowser.open(
                    construct_google_map_path(
                        travel_df, geocodes_df, start_lat, start_lon
                    )
                )
                exit()
            else:
                exit()


def generate_travel_route(
    travel_df, geocodes_df, start_lat, start_lon, distance_to_start, total_distance,
):
    """
    Format a detailed list of breweries visited on the travel route
    """
    s = ""
    number_of_breweries = travel_df["brewery_id"].count()
    s += f"Found {number_of_breweries} beer factories:\n"
    s += f"-> HOME: {start_lat} {start_lon}\n"
    for row in travel_df.itertuples():
        lat, lon = geocodes_df.loc[row.brewery_id, "latitude":"longitude"]
        name = geocodes_df.loc[row.brewery_id, "name"]
        if len(name) > 22:
            name = name[:22] + "..."
        s += f"-> [{row.brewery_id}] {name}: {lat} {lon} Distance: {row.distance} km.\n"
    s += f"<- HOME: {start_lat}, {start_lon} Distance: {distance_to_start} km.\n\n"
    s += f"Total distance: {total_distance} km.\n"
    return s


def generate_beer_list(travel_df, beers_df):
    """
    Format a detailed list of beer types collected on the travel route
    """
    s = ""
    s += f"Collected {count_beer(travel_df)} beer types:\n"
    for row in travel_df.itertuples():
        for name in beers_df.loc[[row.brewery_id], "name"].values:
            s += f"     -> {name}\n"
    return s


def count_beer(travel_df):
    """
    Count how many types of beer each brewery has
    """
    number_of_beers = 0
    for row in travel_df.itertuples():
        beers = geocodes_df.loc[row.brewery_id, "beer_count"]
        number_of_beers += beers
    return int(number_of_beers)


def construct_google_map_path(travel_df, geocodes_df, start_lat, start_lon):
    """
    Make a web string for google maps
    """
    web_str = "http://www.google.com/maps/dir/"
    web_str += f"{start_lat},{start_lon}/"
    for row in travel_df.itertuples():
        lat, lon = geocodes_df.loc[row.brewery_id, "latitude":"longitude"]
        web_str += f"{lat},{lon}/"
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
    geocodes_df = geocodes_df.join(beer_count)

    main()
