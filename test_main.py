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
    lat3, lon3 = 50.709439, 20.355271

    result1 = calculate_distance(lat1, lon1, lat2, lon2)
    result2 = calculate_distance(lat1, lon1, lat3, lon3)
    result3 = calculate_distance(lat2, lon2, lat3, lon3)

    expected1, expected2, expected3 = 82, 650, 568

    assert result1 == expected1
    assert result2 == expected2
    assert result3 == expected3


def test_generate_travel_route():
    data1 = [
        [0, 0, "HOME", 21, 51, 0, 0, 0],
        [22, 200, "Kaunas", 22, 52, 1, 200, 1],
        [33, 100, "Vilnius", 22, 53, 2, 300, 2],
        [0, 300, "HOME", 21, 51, 0, 300, 0],
    ]
    data2 = [
        [0, 0, "HOME", 21, 51, 0, 0, 0],
        [22, 200, "Kaunas", 22, 52, 1, 200, 1],
        [15, 300, "KlaipedaKlaipedaKlaipeda", 22, 53, 2, 300, 2],
        [0, 150, "HOME", 21, 51, 0, 150, 0],
    ]
    data3 = [
        [0, 0, "HOME", 21, 51, 0, 0, 0],
        [22, 200, "Kaunas", 22, 52, 1, 200, 1],
        [15, "300", "Klaipeda", 22, 53, 2, 300, 2],
        [0, 150, "HOME", 21, 51, 0, 150, 0],
    ]

    travel_df1 = pd.DataFrame(
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
        data=data1,
    )
    travel_df2 = pd.DataFrame(
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
        data=data2,
    )
    travel_df3 = pd.DataFrame(
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
        data=data3,
    )

    formatted_string1 = generate_travel_route(travel_df1)
    formatted_string2 = generate_travel_route(travel_df2)

    expected1 = (
        "Found 2 beer factories:\n"
        "-> [0] HOME: 21 51 Distance: 0 km.\n"
        "-> [22] Kaunas: 22 52 Distance: 200 km.\n"
        "-> [33] Vilnius: 22 53 Distance: 100 km.\n"
        "-> [0] HOME: 21 51 Distance: 300 km.\n"
        "\nTotal distance: 600 km.\n"
    )
    expected2 = (  # Case to check if names are shortened
        "Found 2 beer factories:\n"
        "-> [0] HOME: 21 51 Distance: 0 km.\n"
        "-> [22] Kaunas: 22 52 Distance: 200 km.\n"
        "-> [15] KlaipedaKlaipedaKlaipe...: 22 53 Distance: 300 km.\n"
        "-> [0] HOME: 21 51 Distance: 150 km.\n"
        "\nTotal distance: 650 km.\n"
    )

    assert formatted_string1 == expected1
    assert formatted_string2 == expected2
    with pytest.raises(TypeError):
        generate_travel_route(travel_df3)


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
        columns=["brewery_id", "name"],
        data=[[22, "Pilsner"], [33, "Weissbier"], [33, "Dark"]],
    )
    beers_df = beers_df.set_index("brewery_id")
    formatted_string = generate_beer_list(travel_df, beers_df)
    expected = (
        "\nCollected 3 beer types:\n"
        "     -> Pilsner\n"
        "     -> Weissbier\n"
        "     -> Dark\n"
    )
    no_id_beers_df = pd.DataFrame(
        columns=["brewery_id", "name"],
        data=[[25, "Pilsner"], [33, "Weissbier"], [33, "Dark"]],
    )
    no_id_beers_df = no_id_beers_df.set_index("brewery_id")

    with pytest.raises(KeyError):
        generate_beer_list(travel_df, no_id_beers_df)
    assert formatted_string == expected


def test_construct_google_map_path():
    data1 = [
        [0, 0, "HOME", 21, 51, 0, 0, 0],
        [22, 200, "Kaunas", 22, 52, 1, 200, 1],
        [33, 100, "Vilnius", 22, 53, 2, 300, 2],
        [0, 300, "HOME", 21, 51, 0, 600, 0],
    ]
    data2 = [
        [0, 0, "HOME", 21, 51, 0, 0, 0],
        [22, 200, "Kaunas", 22, 52, 1, 200, 1],
        [15, 300, "Klaipeda", 22, 54, 2, 300, 2],
        [0, 150, "HOME", 21, 51, 0, 150, 0],
    ]

    travel_df1 = pd.DataFrame(
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
        data=data1,
    )
    travel_df2 = pd.DataFrame(
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
        data=data2,
    )

    path1 = construct_google_map_path(travel_df1)
    path2 = construct_google_map_path(travel_df2)

    expected1 = "http://www.google.com/maps/dir/21,51/22,52/22,53/21,51/"
    expected2 = "http://www.google.com/maps/dir/21,51/22,52/22,54/21,51/"

    assert path1 == expected1
    assert path2 == expected2
