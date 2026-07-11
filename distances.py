"""
Calulate distances between two of bars and save into database
"""
"""
Please refer to the documentation:
https://developers.google.com/maps/documentation/distance-matrix/distance-matrix?hl=en
"""

import os, requests

from cs50 import SQL
from dotenv import load_dotenv

db = SQL("sqlite:///bar.db")

load_dotenv()
api_key = os.getenv("API_KEY")

base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

def get_info(origins_location, destinations_location):
    """GET infmation from GOOGLE Distance Matrix API"""

    params = {
        "origins": origins_location,
        "destinations": destinations_location,
        "mode": "walking",
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request error: {response.status_code}")
        return None


bars_db = db.execute("SELECT id, longitude AS x, latitude AS y FROM bars")
# Chose a bar as origins and get it's loction
for origins_bar in bars_db:

    # Get origins bar's loction
    origins_bar_location = f"{origins_bar["y"]},{origins_bar["x"]}"

    # Get others bars' loctions
    others_bars_list = []
    destinations_bars_id = []
    for destinations_bar in bars_db:
        if origins_bar["id"] != destinations_bar["id"]:
            # Record destinations bar id
            destinations_bars_id.append(destinations_bar["id"])

            # GET others bars' loctions
            others_bars_location = f"{destinations_bar["y"]},{destinations_bar["x"]}"
            others_bars_list.append(others_bars_location)
    others_bars_loctions = "|".join(others_bars_list)

    # GET info
    data = get_info(origins_bar_location, others_bars_loctions)
    
    # Save data into database
    if data:
        print(f"{data}")
        elements = data["rows"][0]["elements"]

        # Save data into database for each pair of origins and destinations
        for i in range(len(destinations_bars_id)):
            pair_result = elements[i]

            if pair_result["status"] == "OK":
                destinations_bar_id = destinations_bars_id[i]
                distance = pair_result["distance"]["value"]          # NOTE: The unit of distance is the meter.
                time_required = pair_result["duration"]["value"]     # NOTE: The unit of duration is the second.
                db.execute("INSERT INTO distances (origin_bar_id, destination_bar_id, distance, time_required) VALUES (?, ?, ?, ?)", origins_bar["id"], destinations_bar_id, distance, time_required)
