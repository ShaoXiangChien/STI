# Streamlit Timeline Component Example
import streamlit as st
from streamlit_timeline import timeline
import json
from datetime import datetime as dt

# use full page width
st.set_page_config(page_title="Timeline Example", layout="wide")
st.title("Timeline of 反送中")
with open("timeline.json") as fh:
    timeline_dt = json.load(fh)


data = {
    "events": []
}
for k, v in timeline_dt.items():
    time_obj = dt.strptime(k, "%Y-%m-%dT%H:%M:%SZ")
    date = {
        "year": time_obj.year,
        "month": time_obj.month,
        "day": time_obj.day,
    }
    text = {
        "text": v
    }
    data['events'].append({
        "start_date": date,
        "text": text
    })


# st.write(timeline_dt)


# render timeline
timeline(data, height=300)
