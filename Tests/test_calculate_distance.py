import pytest
import pandas as pd
import sys
sys.path.append("../")
from main import calculate_distance


def test_calculate_distance1():
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