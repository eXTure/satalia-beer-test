import argparse
import csv
import sys
import time
import webbrowser
import pandas as pd
from math import asin, cos, radians, sin, sqrt

# Radius of earth in kilometers.
EARTH_RADIUS = 6371

# If set to TRUE, results will be exported to google maps
GOOGLE_MAPS_EXPORT = False

# Max distance you want to travel, in kilometers
MAX_DISTANCE = 2000


def main():
    start_time = time.perf_counter()
    lat = start_lat
    lon = start_lon
    distances_df = pd.DataFrame()
    home_location = {
        "brewery_id": 0,
        "distance": 0,
        "name": "HOME",
        "latitude": start_lat,
        "longitude": start_lon,
        "beer_count": 0,
        "distance_to_home": 0,
        "ratio": 0,
    }
    travel_df = pd.DataFrame(
        columns=[
            "brewery_id",
            "distance",
            "name",
            "latitude",
            "longitude",
            "beer_count",
            "distance_to_home",
            "ratio",
        ],
        data=[home_location],
    )

    while True:

        # Apply the distance calculation formula
        distances_df = (
            geocodes_df.query("Visited == False")  # .query("distance < 1000")
            .apply(apply_distance_calc, args=(lat, lon), axis=1)
            .rename("distance")
            .to_frame()
        )
        # Apply max distance limitations
        one_way_max = MAX_DISTANCE / 2
        distances_df = distances_df.query("distance < @one_way_max")

        # Join additional data from geocodes to distances_df
        distances_df = distances_df.join(
            geocodes_df[["name", "latitude", "longitude", "beer_count"]],
            on="brewery_id",
            how="inner",
        )
        # Calculate how many km you can still travel and get next valid location
        km_left = MAX_DISTANCE - travel_df.distance.sum()
        next_valid_location = get_next_location(distances_df, km_left)

        if next_valid_location.empty:
            # Add HOME location to the end of the completed dataframe
            travel_df = travel_df.append([home_location], ignore_index=True)
            travel_df.iat[-1, 1] = travel_df.tail(2).distance_to_home.values[0]
            break
        else:
            # Add next valid location to the travel dataframe
            travel_df = travel_df.append(next_valid_location)
            lat, lon = next_valid_location[["latitude", "longitude"]].values
            geocodes_df.loc[next_valid_location.brewery_id, "Visited"] = True

    # Show results in terminal
    print(report(travel_df, start_time))

    if GOOGLE_MAPS_EXPORT:
        google_maps(travel_df)


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
    best_next_location = distances_df.ratio.idxmax()
    if distances_df.loc[best_next_location, "distance_to_home"] > km_left:
        return pd.Series(dtype="float64")
    else:
        distances_df = distances_df.rename_axis("brewery_id").reset_index()
        return pd.Series(
            distances_df.loc[distances_df["brewery_id"] == best_next_location].squeeze()
        )


def report(travel_df, start_time):
    """
    Print out the results
    """
    report_str = ""
    if len(travel_df.index) > 2:
        report_str += generate_travel_route(travel_df)
        report_str += generate_beer_list(travel_df, beers_df)
        report_str += f"\nProgram took: {time.perf_counter() - start_time} seconds"
        return report_str
    else:
        report_str += f"Sorry, no breweries within {MAX_DISTANCE}km from this starting location."
        report_str += f"\nProgram took: {time.perf_counter() - start_time} seconds"
        return report_str


def generate_travel_route(travel_df):
    """
    Format a detailed list of breweries visited on the travel route
    """
    s = ""
    number_of_breweries = len(travel_df.index) - 2
    s += f"Found {number_of_breweries} beer factories:\n"
    for _, br_id, distance, name, lat, lon, _, _, _ in travel_df.itertuples():
        if len(name) > 22:
            name = name[:22] + "..."
        s += f"-> [{br_id}] {name}: {lat} {lon} Distance: {distance} km.\n"
    s += f"\nTotal distance: {travel_df.distance.sum()} km.\n"
    return s


def generate_beer_list(travel_df, beers_df):
    """
    Format a detailed list of beer types collected on the travel route
    """
    s = ""
    s += f"\nCollected {travel_df.beer_count.sum()} beer types:\n"
    for row in travel_df.query("brewery_id != 0").itertuples():
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
        google_path = construct_google_map_path(travel_df)
        webbrowser.open(google_path)
        exit()


def construct_google_map_path(travel_df):
    """
    Make a web string for google maps
    """
    web_str = "http://www.google.com/maps/dir/"
    for row in travel_df.itertuples():
        web_str += f"{row.latitude},{row.longitude}/"
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
