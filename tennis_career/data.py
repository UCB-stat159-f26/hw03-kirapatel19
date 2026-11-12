import json
import re

import pandas as pd
import requests


def _extract_matches(js_text):
    """Extract match records from the downloaded JavaScript text."""
    match = re.search(r"var\s+morematchmx\s*=\s*", js_text)
    if match is None:
        raise ValueError("No career match data found in the JavaScript file.")
    try:
        records, _ = json.JSONDecoder().raw_decode(js_text[match.end():].lstrip())
    except json.JSONDecodeError as error:
        raise ValueError("The career match data could not be read.") from error
    return records

def _get_opponent_age(values, match_dates):
    """Convert opponent birth dates or numeric ages into ages."""
    values = values.astype("string").str.strip()
    is_birth_date = values.str.fullmatch(r"\d{8}", na=False)
    birth_dates = pd.to_datetime(
        values.where(is_birth_date), format="%Y%m%d", errors="coerce"
    )
    calculated_ages = (match_dates - birth_dates).dt.days / 365.25
    numeric_ages = pd.to_numeric(values, errors="coerce").astype("Float64")
    return numeric_ages.where(~is_birth_date, calculated_ages)


def _clean_matches(records, player_birth_date):
    """Create a clean match table with player and opponent ages."""
    raw = pd.DataFrame(records)
    matches = raw[[0, 4, 11, 16]].copy()
    matches.columns = ["match_date", "result", "opponent", "opponent_age"]
    matches["match_date"] = pd.to_datetime(
        matches["match_date"], format="%Y%m%d", errors="coerce"
    )
    matches["opponent_age"] = _get_opponent_age(
        matches["opponent_age"], matches["match_date"]
    )
    birth_date = pd.to_datetime(player_birth_date)
    matches["player_age"] = (
        matches["match_date"] - birth_date
    ).dt.days / 365.25
    matches["age_difference"] = matches["player_age"] - matches["opponent_age"]
    matches = matches[matches["result"].isin(["W", "L"])]
    return matches.dropna(
        subset=["match_date", "player_age", "opponent_age"]
    ).reset_index(drop=True)