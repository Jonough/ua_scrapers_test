# Python Standard Library Imports
import time
import streamlit as st
import numpy as np
import requests

# Third Party Imports
import pandas as pd
import airportsdata

# Local Imports
from ua_scrapers_ref import *
from ot_scraper_engine import *

# Global Variables
AIRPORTS = airportsdata.load('IATA')  # vs ICAO

# Convert dataframe to csv, cached so Streamlit doesn't re-run this every time we do something
@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def process_ot(bid_month, cats):
    st.write(bid_month)
    l = len(cats)
    i = 0
    prog = st.progress(0)

    initialize_session(st.session_state.skey)
    
    # Dataframe of OT
    df = pd.DataFrame()
    for cat in cats:
        prog.progress(i/l, f'{cat[0]}{cat[1]}{cat[2]}')
        i += 1

        ot = extract_ot_list(st.session_state.skey, cat, bid_month)
        if ot.empty:
            pass # Generate warning - either no open time or bad html after 3 tries
        else:
            ot['Category'] = str(cat[0]) + str(cat[1]) + str(cat[2])
            df = pd.concat((df, ot), ignore_index=True)
        
    prog.progress(100, "Done!")

    ot_index = ['Pairing Number', 'Category', 'Pairing Date', 'Pay Time']
    df = df[ot_index]
    return df

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
    bid_month = st.selectbox("Bid Months", BID_MONTHS)

    # Submit button
    submit = st.form_submit_button()

# On Submit
if submit:
    # Save the skey to a session state variable to maintain it during re-runs
    if match := re.match(SKEY_RE, ccs_url):
        st.session_state.skey = match.group('skey')
    else:
        st.write("Not a valid CCS URL!")

    # If we have a valid session key, do the rest
    if st.session_state.skey:
        st.write(f'Your Session Key: {st.session_state.skey}')
        with st.container(border=True):
            # Only run this once per session, we don't want CCS to get angry 😡
            if 'open_time' not in st.session_state:
                st.session_state.open_time = process_ot(bid_month, ALL_CATS[:3])
                st.write(st.session_state.open_time)
            else:
                st.write(st.session_state.open_time)
        with st.container(border=True):
            if(all):
                visualizer(BASES_W_FLEETS.keys())
            else:
                visualizer(selected_bases)
