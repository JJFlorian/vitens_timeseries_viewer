import requests
from datetime import datetime

import pandas as pd

from config import VITENS_LIZARD_UUID,LIZARD_API_URL

def get_lizard_locations(search_input:str) -> dict[str, str]:
    """Returns all Lizard locations based on a location name search input string."""
    url = f"{LIZARD_API_URL}/locations/?organisation__uuid={VITENS_LIZARD_UUID}&name__startswith={search_input}&limit=1000"

    locations = {}

    while url:
        r = requests.get(url=url)
        data = r.json()
        url = data.get("next")

        for location in data.get("results", []):
            name = location.get("name")
            uuid = location.get("uuid")
            if name and uuid:
                locations[name] = uuid

    return locations

def get_lizard_timeseries(location_uuid:str) -> dict[str, str]:
    """Fetches all timeseries related to a location."""
    url = f"{LIZARD_API_URL}/timeseries/?location__uuid={location_uuid}&limit=250"

    timeseries = {}

    while url:
        r = requests.get(url=url)
        data = r.json()
        url = data.get("next")

        for timeserie in data.get("results", []):
            name = timeserie.get("name")
            uuid = timeserie.get("uuid")
            if name and uuid:
                timeseries[name] = uuid

    return timeseries


def get_timeserie_metadata(timeserie_uuid:str) -> dict[str, any]:
    """Fetches the metadata of a selected timeserie."""
    url = f"{LIZARD_API_URL}/timeseries/{timeserie_uuid}"

    r = requests.get(url)

    return r.json()

def get_event_data(timeserie_uuid:str, start: datetime, end: datetime, window: str) -> pd.DataFrame:
    """Fetches all event data based on the user input."""
    url = f"{LIZARD_API_URL}/timeseries/{timeserie_uuid}/aggregates?fields=time,avg&start={start}&end={end}&window={window}"

    r = requests.get(url)

    return pd.DataFrame(r.json()["results"])