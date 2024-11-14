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

# Make it look pretty (try to anyway..)
st.set_page_config(page_title='UA Scrapers Test')
st.logo(image='SSCLogoLowRes.png', size='large')
st.title('UA Scrapers')

# Cache so it doesn't re-run every time
@st.cache_data
def add_credit_hours(open_time):
    return calculate_ot_totals(open_time)


def process_ot(skey, cats, bid_month):
    st.write(bid_month)
    l = len(cats)
    i = 0
    prog = st.progress(0)

    initialize_session(skey)

    # Dataframe of OT
    df = pd.DataFrame()
    for cat in cats:
        prog.progress(i/l, f'{cat[0]}{cat[1]}{cat[2]}')
        i += 1

        ot = extract_ot_list(skey, cat, bid_month)
        if ot.empty:
            pass  # Generate warning - either no open time or bad html after 3 tries
        else:
            ot['Category'] = str(cat[0]) + str(cat[1]) + str(cat[2])
            df = pd.concat((df, ot), ignore_index=True)

    prog.progress(100, "Done!")
    # It didn't crash! Make sure the user sees this
    time.sleep(2)

    # If it's empty just return the empty dataframe, otherwise add the columns
    if not df.empty:
        ot_index = ['Pairing Number', 'Category', 'Pairing Date', 'Pay Time']
        df = df[ot_index]

    return df


def visualizer(selected_bases):
    # Follow a color scheme for each base (better color scheme pending)
    colors = {
        'EWR':   (255, 0, 0),
        'DCA':   (255, 0, 0),
        'MCO':   (255, 0, 0),
        'CLE':   (255, 0, 0),
        'ORD':   (255, 0, 0),
        'IAH':   (255, 0, 0),
        'DEN':   (255, 0, 0),
        'LAS':   (255, 0, 0),
        'LAX':   (255, 0, 0),
        'SFO':   (255, 0, 0),
        'GUM':   (255, 0, 0)
    }

    # Generate a list of base, lat, long for each of our bases
    data = [(base, AIRPORTS[base]['lat'], AIRPORTS[base]['lon'], colors[base])
            for base in selected_bases]

    # Turn that into a beautiful dataframe with column names that works with streamlit map
    ua_bases = pd.DataFrame(data, columns=['Base', 'lat', 'lon', 'color'])

    # Plot it with minimal effort
    st.map(ua_bases, color='color')


# No form data submitted - all validation should happen in this 'branch'
if 'ot_form' not in st.session_state:
    # Form
    with st.form(key='skey_getter', border=True,
                 enter_to_submit=True, clear_on_submit=False):
        ccs_url = st.text_area("Enter any CCS URL:")

        # Bases multiselect with all option:
        all = st.checkbox("Select all bases")
        st.write("OR")
        selected_bases = st.multiselect("Select one or more options:",
                                        BASES_W_FLEETS)

        # Bid month dropdown - default to NOV2024
        bid_month = st.selectbox("Bid Month", BID_MONTHS, index=1)

        # Submit button
        if st.form_submit_button():
            # If all selected, fill in selected bases
            if (all):
                selected_bases = list(BASES_W_FLEETS.keys())

            # Check valid skey can be extracted from URL
            if match := re.match(SKEY_RE, ccs_url):
                # If no bases, prompt user to enter at least one
                if not selected_bases:
                    st.write("Please select at least one base!")
                else:
                    # All inputs are valid, save them to a tuple and rerun the script
                    st.session_state.ot_form = (match.group(
                        'skey'), selected_bases, bid_month)
                    st.rerun()
            else:
                st.write("Not a valid CCS URL!")
# We have form data submitted and validated, do the rest
else:
    # Unpack the ot_form results:
    skey, selected_bases, bid_month = st.session_state.ot_form

    # Turn selected bases into a list of selected categories by filtering all categories
    selected_cats = list(filter(lambda c: c[0] in selected_bases, ALL_CATS))

    # Convert to text to use in a dropdown of selected categories
    selected_cats_text = [f'{c[0]}{c[1]}{c[2]}' for c in selected_cats]

    with st.container(border=True):
        # Only run this once per session, we don't want CCS to get angry 😡 branching should take care of this
        if 'open_time' not in st.session_state:
            st.write(f'Your Session Key: {skey}')

            st.session_state.open_time = process_ot(
                skey, selected_cats, bid_month)
            st.rerun()
        # Once we have the open time, the script will branch into displaying the results
        else:
            # Left side
            left, right = st.columns(2)
            open_time = st.session_state.open_time
            left.write(open_time)

            # Right side
            category_viewer = right.selectbox('Category', selected_cats_text)
            ot_total_credit, ot_trip_count = add_credit_hours(open_time)
            selected_credit, no_trips = ot_total_credit[category_viewer], ot_trip_count[category_viewer]

            st.write("Trip Count")
            df = pd.DataFrame(ot_trip_count.items(), columns=['Category', 'Trip Count'])
            df.set_index('Category', inplace=True)
            
            #ot_trip_count_df = pd.DataFrame(ot_trip_count, columns=['Category', 'Trip Count'])
            #ot_trip_count_df.set_index('Category')
            #st.bar_chart(ot_trip_count_df)
            right.write(f'Total Credit Hours for {category_viewer}: {selected_credit}')
            right.write(f'Total Number of Trips: {no_trips}')
            
            st.bar_chart(df, horizontal=True)
            st.write(df)

            # Below is the visualizer (map, graph etc.)
            visualizer(selected_bases)
