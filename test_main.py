import pytest
import pandas as pd
from main import calculate_distance
from main import apply_distance_calc
from main import calculate_ratio
from main import get_next_location
from main import generate_travel_route
from main import generate_beer_list
from main import construct_google_map_path


def test_calculate_distance():
    pass


def test_apply_distance_calc():
    pass


def test_calculate_ratio():
    pass


def test_get_next_location():
    pass


def test_generate_travel_route():
    travel_df = pd.DataFrame(columns=["brewery_id", "distance"], data=[[0, 5], [1, 7]])
    geocodes_df = pd.DataFrame(
        columns=["brewery_id", "latitude", "longitude"], data=[[0, 1, 2], [1, 3, 4]]
    )
    breweries_df = pd.DataFrame(columns=["name"], data=[["Kaunas"], ["Vilnius"]])
    formatted_string = generate_travel_route(travel_df)

    expected = (
        ""
        "Found 2 beer factories:\n"
        "-> HOME: 10 12\n"
        "-> [0] Kaunas: 1 2 Distance: 5 km.\n"
        "-> [1] Vilnius: 3 4 Distance: 7 km.\n"
        "<- HOME: 10, 12 Distance: 5 km.\n\n"
        "Total distance: 10 km.\n"
    )

    assert formatted_string == expected


def test_generate_beer_list():
    travel_df = pd.DataFrame(columns=["brewery_id"], data=[[0], [1]])
    beers_df = pd.DataFrame(
        columns=["brewery_id", "name"], data=[[0, "Pilsner"], [1, "Weissbier"]]
    )
    formatted_string = generate_beer_list(travel_df, beers_df)
    expected = "Collected 2 beer types:\n" "     -> Pilsner\n" "     -> Weissbier\n"

    assert formatted_string == expected


def test_construct_google_map_path():
    travel_df = pd.DataFrame(columns=["brewery_id"], data=[[0], [1]])
    geocodes_df = pd.DataFrame(columns=["latitude", "longitude"], data=[[1, 3], [3, 4]])
    path = construct_google_map_path(travel_df)
    assert path == "http://www.google.com/maps/dir/10,12/1,3/3,4/10,12/"
