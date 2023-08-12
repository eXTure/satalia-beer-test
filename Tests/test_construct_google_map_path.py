import pytest
import pandas as pd
import sys
sys.path.append("../")
from main import construct_google_map_path


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
