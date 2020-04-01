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
    lat1, lon1 = 51.355468, 11.100790
    lat2, lon2 = 51.268215, 12.276850
    result = calculate_distance(lat1, lon1, lat2, lon2)
    expected = 82
    assert result == expected


def test_generate_travel_route():
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
        data=[
            [0, 0, "HOME", 21, 51, 0, 0, 0],
            [22, 200, "Kaunas", 22, 52, 1, 200, 1],
            [33, 100, "Vilnius", 22, 53, 2, 300, 2],
            [0, 300, "HOME", 21, 51, 0, 600, 0],
        ],
    )
    formatted_string = generate_travel_route(travel_df)

    expected = (
        "Found 2 beer factories:\n"
        "-> [0] HOME: 21 51 Distance: 0 km.\n"
        "-> [22] Kaunas: 22 52 Distance: 200 km.\n"
        "-> [33] Vilnius: 22 53 Distance: 100 km.\n"
        "-> [0] HOME: 21 51 Distance: 300 km.\n"
        "\nTotal distance: 600 km.\n"
    )

    assert formatted_string == expected


def test_generate_beer_list():
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
        data=[
            [0, 0, "HOME", 21, 51, 0, 0, 0],
            [22, 200, "Kaunas", 22, 52, 1, 200, 1],
            [33, 100, "Vilnius", 22, 53, 2, 300, 2],
            [0, 300, "HOME", 21, 51, 0, 600, 0],
        ],
    )
    beers_df = pd.DataFrame(
        columns=["brewery_id", "name"], data=[[22, "Pilsner"], [33, "Weissbier"], [33, "Dark"]]
    )
    formatted_string = generate_beer_list(travel_df, beers_df)
    expected = (
        "\nCollected 3 beer types:\n"
        "     -> Pilsner\n"
        "     -> Weissbier\n"
        "     -> Dark\n"
    )
    
    assert formatted_string == expected


def test_construct_google_map_path():
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
        data=[
            [0, 0, "HOME", 21, 51, 0, 0, 0],
            [22, 200, "Kaunas", 22, 52, 1, 200, 1],
            [33, 100, "Vilnius", 22, 53, 2, 300, 2],
            [0, 300, "HOME", 21, 51, 0, 600, 0],
        ],
    )
    path = construct_google_map_path(travel_df)
    expected = "http://www.google.com/maps/dir/21,51/22,52/22,53/21,51/"
    
    assert path == expected
