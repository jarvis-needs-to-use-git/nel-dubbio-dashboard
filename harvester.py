import json
import os
import sys
from datetime import datetime, date, timedelta
from spotifyconnector import SpotifyConnector
from appleconnector import AppleConnector

def harvest():
    secrets_path = os.path.join(os.path.dirname(__file__), "secrets.json")
    data_path = os.path.join(os.path.dirname(__file__), "data.json")

    # Try local secrets first, then fall back to streamlit secrets (for cloud)
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            secrets = json.load(f)
    else:
        try:
            import streamlit as st
            secrets = st.secrets
        except:
            print("No secrets found. Please provide secrets.json or set streamlit secrets.")
            return

    results = {
        "timestamp": datetime.now().isoformat(),
        "spotify": {},
        "apple": {}
    }

    # Harvest Spotify
    try:
        s_conf = secrets.get("spotify", {})
        if s_conf.get("podcast_id") != "FILL_ME_IN":
            connector = SpotifyConnector(
                base_url="https://generic.wg.spotify.com/podcasters/v0",
                client_id=s_conf["client_id"],
                podcast_id=s_conf["podcast_id"],
                sp_dc=s_conf["sp_dc"],
                sp_key=s_conf["sp_key"]
            )
            # Use metadata or specific stats calls
            results["spotify"]["metadata"] = connector.metadata()
            
            # Use a 30-day window for more reliable stats
            end = date.today()
            start = end - timedelta(days=30)
            
            results["spotify"]["listeners"] = connector.listeners(start=start, end=end)
            results["spotify"]["aggregate"] = connector.aggregate(start=start, end=end)
    except Exception as e:
        results["spotify"]["error"] = str(e)

    # Harvest Apple
    try:
        a_conf = secrets.get("apple", {})
        if a_conf.get("podcast_id") != "FILL_ME_IN":
            connector = AppleConnector(
                podcast_id=a_conf["podcast_id"],
                myacinfo=a_conf["myacinfo"],
                itctx=a_conf["itctx"]
            )
            results["apple"]["overview"] = connector.overview()
            results["apple"]["trends"] = connector.trends()
    except Exception as e:
        results["apple"]["error"] = str(e)

    with open(data_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Data harvested at {results['timestamp']}")

if __name__ == "__main__":
    harvest()
