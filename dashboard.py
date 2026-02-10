import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Nel Dubbio Podcast Dashboard", page_icon="🎙️")

st.title("🎙️ Nel Dubbio Dashboard")

data_path = os.path.join(os.path.dirname(__file__), "data.json")

if not os.path.exists(data_path):
    st.warning("No data found locally.")
    if st.button("🚀 Harvest Data Now"):
        with st.spinner("Connecting to Spotify and Apple..."):
            from harvester import harvest
            harvest()
            st.rerun()
    st.info("Ensure secrets are configured in the Streamlit Cloud console.")
else:
    with open(data_path, "r") as f:
        data = json.load(f)
    
    st.caption(f"Last updated: {data['timestamp']}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟢 Spotify Stats (30d)")
        s_data = data.get("spotify", {})
        if "error" in s_data:
            st.error(f"Error: {s_data['error']}")
        elif s_data:
            metadata = s_data.get("metadata", {})
            st.metric("Total Followers", metadata.get("followers", "N/A"))
            st.metric("Total Starts", metadata.get("starts", "N/A"))
            st.metric("Total Streams", metadata.get("streams", "N/A"))
            
            listeners = s_data.get("listeners", {}).get("counts", [])
            if listeners:
                df_listeners = pd.DataFrame(listeners)
                df_listeners['date'] = pd.to_datetime(df_listeners['date'])
                st.line_chart(df_listeners.set_index('date'))
        else:
            st.info("Spotify data not configured.")

    with col2:
        st.subheader("🟣 Apple Stats (All Time)")
        a_data = data.get("apple", {})
        if "error" in a_data:
            st.error(f"Error: {a_data['error']}")
        elif a_data:
            overview = a_data.get("overview", {})
            play_count = overview.get("showPlayCount", {}).get("latestValue", {})
            st.metric("Total Listeners", play_count.get("uniquelistenerscount", "N/A"))
            st.metric("Followers", overview.get("followerAllTimeTrends", [[0, 0]])[-1][1])
            st.metric("Plays", play_count.get("playscount", "N/A"))
            
            trends = overview.get("showPlayCountTrends", [])
            if trends:
                # Apple trends format is [date, val1, val2, val3]
                df_trends = pd.DataFrame(trends, columns=['date', 'engaged', 'listeners', 'plays'])
                df_trends['date'] = pd.to_datetime(df_trends['date'], format='%Y%m%d')
                st.line_chart(df_trends.set_index('date')[['plays', 'listeners']])
        else:
            st.info("Apple data not configured.")

    st.divider()
    st.write("### Audience Demographics (Spotify 30d)")
    s_agg = s_data.get("aggregate", {})
    if s_agg:
        genders = s_agg.get("genderedCounts", {}).get("counts", {})
        st.bar_chart(pd.Series(genders))

    st.write("### Top Countries (Apple)")
    a_countries = a_data.get("overview", {}).get("showTopCountries", {})
    if a_countries:
        # Simplified mapping
        st.json(a_countries)
