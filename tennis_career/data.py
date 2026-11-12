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


def _extract_birth_date(profile_text):
    """Find the player's birthday on their profile."""
    match = re.search(r"var dob = (\d{8});", profile_text)

    if match is None:
        raise ValueError("Player birth date not found. Check the player name.")

    birthday = pd.to_datetime(match.group(1), format="%Y%m%d", errors="coerce")

    if pd.isna(birthday):
        raise ValueError("The player's birth date is invalid.")

    return birthday

def _format_player_name(player_name):
    """Format a player name for the website."""
    if not isinstance(player_name, str) or not player_name.strip():
        raise ValueError("Please enter a player's name.")

    words = player_name.split()

    if len(words) > 1:
        return "".join(word.capitalize() for word in words)

    return words[0]

def _download_text(url):
    """Download text and report missing pages or connection problems."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            raise ValueError("Player data not found. Check the player name.")
        response.raise_for_status()
    except requests.RequestException as error:
        raise ConnectionError("Could not download data from Tennis Abstract.") from error
    return response.text


def get_player_matches(player_name):
    """Download and clean a player's career matches."""
    name = _format_player_name(player_name)
    base_url = "https://www.tennisabstract.com"

    profile = _download_text(f"{base_url}/cgi-bin/player.cgi?p={name}")
    birthday = _extract_birth_date(profile)

    career = _download_text(f"{base_url}/jsmatches/{name}Career.js")
    records = _extract_matches(career)
    matches = _clean_matches(records, birthday)

    if matches.empty:
        raise ValueError("No matches with usable age data were found.")

    matches.attrs["player_name"] = player_name
    return matches