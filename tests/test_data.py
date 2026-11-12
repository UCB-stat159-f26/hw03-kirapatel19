import pandas as pd
import pytest

from tennis_career.data import _clean_matches, _extract_matches


FEMALE_JS = """
var morematchmx = [
["19951030", "Canadian Open", "Carpet", "W", "L", "", "", "WC",
"Q1", "6-1 6-1", "3", "Anne Miller", "149", "7", "", "R", "19770119"]
]
"""

MALE_JS = """
var morematchmx = [
["20010910", "Spain F10", "Hard", "S", "L", "", "", "WC",
"R32", "2-6 7-5 6-2", "3", "Guillermo Platel", "731", "", "", "R",
"22.264202601"]
]
"""


def test_extract_matches():
    records = _extract_matches(FEMALE_JS)
    assert len(records) == 1
    assert records[0][11] == "Anne Miller"


def test_female_ages():
    matches = _clean_matches(_extract_matches(FEMALE_JS), "1981-09-26")
    row = matches.iloc[0]
    match_date = pd.Timestamp("1995-10-30")
    player_age = (match_date - pd.Timestamp("1981-09-26")).days / 365.25
    opponent_age = (match_date - pd.Timestamp("1977-01-19")).days / 365.25
    assert row["player_age"] == pytest.approx(player_age)
    assert row["opponent_age"] == pytest.approx(opponent_age)
    assert row["age_difference"] == pytest.approx(player_age - opponent_age)
    assert row["result"] == "L"


def test_male_ages():
    matches = _clean_matches(_extract_matches(MALE_JS), "1986-06-03")
    row = matches.iloc[0]
    player_age = (
        pd.Timestamp("2001-09-10") - pd.Timestamp("1986-06-03")
    ).days / 365.25
    assert row["player_age"] == pytest.approx(player_age)
    assert row["opponent_age"] == pytest.approx(22.264202601)
    assert row["age_difference"] == pytest.approx(player_age - 22.264202601)


def test_missing_match_data():
    with pytest.raises(ValueError, match="No career match data"):
        _extract_matches("var unrelated = [];")


def test_invalid_match_data():
    with pytest.raises(ValueError, match="could not be read"):
        _extract_matches("var morematchmx = not_valid_json;")