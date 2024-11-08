import streamlit as st
import pandas as pd
import numpy as np

# Third Party Imports
import airportsdata

# Local Imports
from ua_scrapers_ref import *

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/).")

df = pd.DataFrame({
    'first column': range(0, 100, 2),
    'second column': range(1, 100, 2)
})

# Random Scatter Plot around San Francisco:
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.write(map_data)
st.map(map_data)

"""
bid_month = st.selectbox('Bid Month:', BID_MONTHS)
date = st.date_input('Pick a Day:', 'today')
submit = st.button('Submit')
"""

with st.form("my_form"):
    slider_val = st.slider("Inside the form")
    st.form_submit_button('Submit')
    st.write(slider_val)

# Import airportsdata in IATA format
airports = airportsdata.load('IATA') # vs ICAO

# Generate a list of base, lat, long for each of our bases
data = [(base, airports[base]['lat'], airports[base]['lon']) for base in BASES_W_FLEETS]

# Turn that into a beautiful dataframe with column names
ua_bases = pd.DataFrame(data, columns=['Base', 'lat', 'lon'])

# Plot it with minimal effort
st.map(ua_bases)

st.write(ua_bases)