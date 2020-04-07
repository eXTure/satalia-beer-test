import pytest
import pandas as pd
import sys
sys.path.append("../")
from main import generate_beer_list


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