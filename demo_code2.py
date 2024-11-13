# Python Standard Library Imports
import time
import streamlit as st
import numpy as np

# Third Party Imports
import pandas as pd
import airportsdata

# Local Imports
from ua_scrapers_ref import *

# Global Variables
CCS_SKEY = None
AIRPORTS = airportsdata.load('IATA')  # vs ICAO

# Convert dataframe to csv, cached so Streamlit doesn't re-run this every time we do something
@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def process_ot(cats):
    l = len(cats)
    i = 0
    prog = st.progress(0)
    for cat in cats:
        prog.progress(i/l, f'{cat[0]}{cat[1]}{cat[2]}')
        i += 1
        time.sleep(0.1)
    prog.progress(100, "Done!")
    time.sleep(0.1)

# This will run on submit
def visualizer(selected_bases):
    # Follow a color scheme for each base (better color scheme pending)
    colors = {
        'EWR':   (0, 0, 255),
        'DCA':   (0, 255, 255),
        'MCO':   (255, 0, 0),
        'CLE':   (255, 255, 0),
        'ORD':   (255, 255, 255),
        'IAH':   (255, 255, 255),
        'DEN':   (255, 255, 255),
        'LAS':   (255, 255, 255),
        'LAX':   (255, 255, 255),
        'SFO':   (255, 255, 255),
        'GUM':   (255, 255, 255)
    }

    # Generate a list of base, lat, long for each of our bases
    data = [(base, AIRPORTS[base]['lat'], AIRPORTS[base]['lon'], colors[base])
            for base in selected_bases]

    # Turn that into a beautiful dataframe with column names that works with streamlit map
    ua_bases = pd.DataFrame(data, columns=['Base', 'lat', 'lon', 'color'])

    # Plot it with minimal effort
    st.map(ua_bases, color='color')

    st.write(ua_bases)

# Form
with st.form(key='skey_getter', border=True,
            enter_to_submit=True, clear_on_submit=True):
    ccs_url = st.text_area("Enter any CCS URL:")

    selected_bases = st.multiselect("Select one or more options:",
                                        BASES_W_FLEETS)
    st.write('OR')
    # Bases multiselect with all option:
    all = st.checkbox("Select all bases")        

    # Bid month dropdown
    st.selectbox("Bid Months", BID_MONTHS)

    # Submit button
    submit = st.form_submit_button()

# On Submit
if submit:
    with st.container(border=True):
        if match := re.match(SKEY_RE, ccs_url):
            CCS_SKEY = match.group('skey')
            st.write(f'Your Session Key: {CCS_SKEY}')
        else:
            CCS_SKEY = None
            st.exception("Not a valid CCS URL!")
    with st.container(border=True):
        if(all):
            process_ot(ALL_CATS)
        else:
            process_ot(ALL_CATS[:5])
    with st.container(border=True):
        if(all):
            visualizer(BASES_W_FLEETS.keys())
        else:
            visualizer(selected_bases)
