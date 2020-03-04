import pytest
import pandas as pd
from main import construct_google_map_path
from main import display_travel_route


def test_construct_google_map_path():
    travel_df = pd.DataFrame(columns=["brewery_id"], data=[[0], [1]])
    geocodes_df = pd.DataFrame(columns=["latitude", "longitude"], data=[[0, 1], [1, 3]])
    path = construct_google_map_path(travel_df, geocodes_df)
    assert path == "http://www.google.com/maps/dir/0,1/1,3/"


def test_generate_travel_route():
    travel_df = pd.DataFrame(columns=["brewery_id", "distance"], data=[[0, 5], [1, 7]])
    geocodes_df = pd.DataFrame(
        columns=["brewery_id", "latitude", "longitude"], data=[[0, 1, 2], [1, 3, 4]]
    )
    breweries_df = pd.DataFrame(columns=["name"], data=[["Kaunas"], ["Vilnius"]])
    formatted_string = display_travel_route(travel_df, 5, 10, 3, 4, geocodes_df, breweries_df)

    expected = (
        ""
        "Found 2 beer factories:\n"
        "-> HOME: 3 4\n"
        "-> [0] Kaunas: 1 2 Distance: 5 km.\n"
        "-> [1] Vilnius: 3 4 Distance: 7 km.\n"
        "<- HOME: 3, 4 Distance: 5 km.\n"
        "Total distance: 10 km.\n"
    )

    assert formatted_string == expected
