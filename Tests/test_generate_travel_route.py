import pytest
import pandas as pd
import sys
sys.path.append("../")
from main import generate_travel_route


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