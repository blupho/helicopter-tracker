
import streamlit as st
import pandas as pd
import pydeck as pdk
from FlightRadar24 import FlightRadar24API
from utils import get_bounds, haversine_distance, is_helicopter
import time

# --- Configuration ---
TARGET_LAT = 29.728611
TARGET_LON = -95.1575
RADIUS_MILES = 3.0
REFRESH_RATE_SEC = 30

st.set_page_config(page_title="Helicopter Tracker", layout="wide")

# --- App Header ---
st.title("🚁 Helicopter Tracker")
st.markdown(f"**Target Location:** {TARGET_LAT:.6f}, {TARGET_LON:.6f} (Radius: {RADIUS_MILES} miles)")

# --- State Management ---
if 'last_update' not in st.session_state:
    st.session_state.last_update = 0

# --- Data Fetching ---
# --- Data Fetching ---
@st.cache_data(ttl=REFRESH_RATE_SEC)
def fetch_helicopter_data():
    fr_api = FlightRadar24API()
    
    # Get bounds for API query (add a buffer to ensure we catch everything on the edge)
    bounds = get_bounds(TARGET_LAT, TARGET_LON, RADIUS_MILES + 2.0) 
    
    try:
        flights = fr_api.get_flights(bounds=bounds)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return [], []

    helicopters = []
    trails = []
    
    for flight in flights:
        # Calculate precise distance
        dist = haversine_distance(TARGET_LAT, TARGET_LON, flight.latitude, flight.longitude)
        
        if dist <= RADIUS_MILES:
            # Check if it's a helicopter
            if is_helicopter(flight.aircraft_code):
                flight_data = {
                    "Callsign": flight.callsign,
                    "ICAO": flight.icao_24bit,
                    "Type": flight.aircraft_code,
                    "Registration": flight.registration,
                    "Altitude (ft)": flight.altitude,
                    "Speed (kts)": flight.ground_speed,
                    "Heading": flight.heading,
                    "Lat": flight.latitude,
                    "Lon": flight.longitude,
                    "Distance (mi)": round(dist, 2)
                }
                helicopters.append(flight_data)
                
                # Fetch details for trail (this might add latency, but okay for few target/aircraft)
                try:
                    details = fr_api.get_flight_details(flight)
                    if 'trail' in details:
                        # Extract trail: list of dictionaries with 'lat', 'lng', 'alt'
                        # PyDeck needs list of [lon, lat]
                        path = [[p['lng'], p['lat']] for p in details['trail']]
                        # Add current position as last point
                        path.append([flight.longitude, flight.latitude])
                        
                        trails.append({
                            "Callsign": flight.callsign,
                            "path": path,
                            "color": [0, 255, 0] # Green trail
                        })
                except Exception:
                    pass # Skip trail if fails
                
    return helicopters, trails

# --- Main Logic ---

# Auto-refresh logic placeholder
if st.button("Refresh Now"):
    st.cache_data.clear()
    st.rerun()

data, trails_data = fetch_helicopter_data()
df = pd.DataFrame(data)
df_trails = pd.DataFrame(trails_data)

# --- Visualization ---

# 1. Map
view_state = pdk.ViewState(
    latitude=TARGET_LAT,
    longitude=TARGET_LON,
    zoom=12,
    pitch=0,
)

# Layer for Target
target_layer = pdk.Layer(
    "ScatterplotLayer",
    data=[{"lat": TARGET_LAT, "lon": TARGET_LON}],
    get_position="[lon, lat]",
    get_color=[255, 0, 0, 160], # Red
    get_radius=200,
    pickable=True,
)

layers = [target_layer]

if not df.empty:
    # Layer for Helicopters
    heli_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[Lon, Lat]",
        get_color=[0, 255, 0, 255], # Bright Green
        get_radius=150,
        pickable=True,
    )
    
    # Text Layer for Callsigns
    text_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position="[Lon, Lat]",
        get_text="Callsign",
        get_color=[0, 0, 0, 255],
        get_size=16,
        get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -10]
    )
    
    layers.extend([heli_layer, text_layer])
    
    # Trail Layer
    if not df_trails.empty:
        trail_layer = pdk.Layer(
            "PathLayer",
            data=df_trails,
            get_path="path",
            get_color="color",
            width_min_pixels=3,
            pickable=False
        )
        layers.insert(0, trail_layer) # Draw trails below helicopters
    
    st.success(f"Found {len(df)} helicopter(s) in range!")
else:
    st.info("No helicopters currently detected in range.")

st.pydeck_chart(pdk.Deck(
    initial_view_state=view_state,
    layers=layers,
    tooltip={"text": "{Callsign}\nType: {Type}\nAlt: {Altitude (ft)} ft"}
))

# 2. Data Table
if not df.empty:
    st.markdown("### Detailed Data")
    st.dataframe(df)

# Auto-refresh with time loop (simple implementation for streamlit run)
# NOTE: In a real deployment, st.empty() loops are sometimes discouraged, 
# but for a local verified app they work fine.
time_placeholder = st.empty()
import datetime
time_placeholder.caption(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")

