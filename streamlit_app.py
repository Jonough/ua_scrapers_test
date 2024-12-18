# Python Standard Library Imports
import time
from datetime import datetime
import streamlit as st
import numpy as np
import requests

# Third Party Imports
import pandas as pd

# Local Imports
from ua_scrapers_ref import *
from ot_scraper_engine import *


# Make it look pretty (try to anyway..)
st.set_page_config(
    page_title='UA Scrapers OT')
st.logo(
    image='SSCLogoLowRes.png',
    size='large')
st.title('UA Scrapers - Open Time')

# Cached functions


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


@st.cache_data
def add_credit_hours(open_time):
    return calculate_ot_totals(open_time)


def process_ot(skey, cats, bid_month):
    # Goes through each category and compiles a DataFrame of OT
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
            st.write(
                f'Error with {cat[0]}{cat[1]}{cat[2]}: Connection error or no trips')
            time.sleep(5)  # So user can see the error
        else:
            df = pd.concat((df, ot), ignore_index=True)

    prog.progress(100, "Done!")
    # It didn't crash! Make sure the user sees this
    time.sleep(2)

    return df


# No form data submitted or no file uploaded - all validation should happen in this 'branch'
if ('ot_form' not in st.session_state) and ('open_time' not in st.session_state):
    # Form
    with st.form(key='skey_getter', border=True,
                 enter_to_submit=True, clear_on_submit=False):
        st.write('Enter Data to Scrape CCS Open Time')
        ccs_url = st.text_area('Enter any CCS URL:')

        # Bases multiselect with all option:
        all = st.checkbox('Select all bases')
        st.write('OR')
        selected_bases = st.multiselect('Select one or more options:',
                                        BASES_W_FLEETS)

        # Bid month dropdown - uses stripped bid months (current month onward), default to next month (index 1)
        bid_month = st.selectbox("Bid Month", BID_MONTHS_DT, index=1)

        # File Upload Options
        st.write('OR')
        st.write('Upload Open Time from a CSV File')
        ot_file = st.file_uploader('Choose a file')

        # Submit button
        if st.form_submit_button():
            # First check if the user uploaded a file
            if ot_file is not None:
                try:
                    ot = pd.read_csv(ot_file, dtype=OT_DF_DTYPES)
                    # String to dates:
                    ot['Pairing Date'] = ot['Pairing Date'].apply(lambda d: datetime.strptime(
                        d, '%Y-%m-%d').date())
                    ot['Pairing End Date'] = ot['Pairing End Date'].apply(lambda d: datetime.strptime(
                        d, '%Y-%m-%d').date())
                except:
                    st.write(
                        'Issue reading the file! Please select another file.')
                    time.sleep(3)
                    st.rerun()
                if ot.empty:  # Empty dataframe
                    st.write('No trips in the file! Please select another file.')
                    time.sleep(3)
                    st.rerun()
                if set(OT_DF_FORMAT).issubset(ot.columns):
                    st.session_state.open_time = ot
                    st.rerun()
                else:  # Couldn't find the right columns in the data
                    st.write(
                        'The file is in the incorrect format! Please select another file.')
                    time.sleep(3)
                    st.rerun()

            # No file, so we check if the form inputs are valid

            # If all selected, fill in selected bases
            if (all):
                selected_bases = list(BASES_W_FLEETS.keys())

            # Check valid skey can be extracted from URL
            if match := re.match(SKEY_RE, ccs_url):
                # If no bases, prompt user to enter at least one
                if not selected_bases:
                    st.write('Please select at least one base!')
                else:
                    # All inputs are valid, save them to a cached tuple and rerun the script
                    st.session_state.ot_form = (match.group(
                        'skey'), selected_bases, bid_month)
                    st.rerun()
            else:
                st.write('Not a valid CCS URL!')
# We have form data submitted and validated, do the rest
else:
    # Form data was submitted and no file was uploaded, so scrape the open time list
    if 'open_time' not in st.session_state:
        # Unpack the ot_form results:
        skey, selected_bases, bid_month = st.session_state.ot_form

        # Turn selected bases into a list of selected categories by filtering all categories
        selected_cats = list(
            filter(lambda c: c[0] in selected_bases, ALL_CATS))

        with st.container(border=True):
            # Only run this once per session, we don't want CCS to get angry 😡 branching should take care of this
            st.write(f'Your Session Key: {skey}')

            st.session_state.open_time = process_ot(
                skey, selected_cats, bid_month)

            st.rerun()

    # copy of existing open time
    open_time = st.session_state.open_time

    if 'selected_cats_text' not in st.session_state:
        # Generate list of categories adding an ALL option
        st.session_state.selected_cats_text = open_time['Category'].unique(
        ).tolist()
        st.session_state.selected_cats_text.insert(0, 'ALL')

    if 'bid_month' not in st.session_state:
        # Figure out the bid month
        d = open_time['Pairing Date'].iloc[0]  # Date of first pairing
        st.session_state.bid_month = date_to_bidmonth(d)

    selected_cats_text = st.session_state.selected_cats_text

    bid_month = st.session_state.bid_month
    st.write(bid_month)

    with st.container(border=True):
        if open_time.empty:
            st.write(
                "Nothing in Open Time! Here's a pretty map you can play with while you figure out what went wrong:")
            st.map()
        else:
            # This is the main branch that displays everything

            

            # Take the open_time dataframe and save it to a csv with the bid month as file name
            ot_csv = convert_df(open_time)
            st.download_button('Download Entire Trip List', ot_csv,
                               file_name=f'{bid_month}.csv')

            # Category Filter
            selected_category = st.selectbox('Category', selected_cats_text)

            # For displaying filtered results
            trip_list = open_time.copy()

            if (selected_category != 'ALL'):
                # Filter selected category
                trip_list = trip_list[trip_list['Category']
                                      == selected_category]

            if st.checkbox('Show Carryover Trips Only'):
                # Filter carryover if pairing end date is past the end of the bid month
                trip_list = trip_list[trip_list['Pairing End Date']
                                      > BID_MONTHS_DT[bid_month][1]]

            st.write('Trip List')
            # Don't display these columns to the user
            st.write(trip_list.drop(
                ['Pairing End Date', 'Pay Minutes'], axis=1))

            # Initialize streamlit columns
            left, right = st.columns(2, gap='small')

            # Left Side
            ot_totals = add_credit_hours(open_time)
            # df = pd.DataFrame.from_dict(ot_totals, orient='index', columns=[
            #                            'Trip Count', 'Total Credit'])
            # df.index.name = 'Category'
            left.write('Totals')
            left.write(ot_totals.drop('Pay Minutes', axis=1))

            with right.container(border=True):
                selected_cat = st.selectbox(
                    'Select Category', selected_cats_text[1:])  # without ALL
                # Carryover adjustment
                co_adj = st.text_input('Enter Carryover Adjustment Here:')
                cat_credit = st.text_input(
                    'Enter Category Total Credit:')  # Total category credit
                if st.button('Submit'):
                    co_adj = dur_to_mins(co_adj)
                    cat_credit = dur_to_mins(cat_credit)
                    if (co_adj == 0) or (cat_credit == 0):
                        st.write(
                            'Please enter a valid CO adjustment and total credit in hhh:mm format')
                    else:
                        # Deduct the carryover adjustment and display it
                        adj_credit = int(
                            ot_totals['Pay Minutes'][selected_cat] - co_adj)
                        st.write(
                            f'Total without carry-over: {mins_to_dur(adj_credit)}')
                        
                        # Calculate the percentage of open time credit and display it (2 decimal places)
                        percentage = ((adj_credit / cat_credit)*100)
                        st.write(f'Percentage of credit in open time: {percentage:.2f}')

            # Try to plot trip totals:

            st.write("Trip Count")
            st.bar_chart(ot_totals.drop(labels=['Total Credit', 'Pay Minutes'],
                                        axis=1), horizontal=True)

            st.write("Total Pay Minutes")
            st.bar_chart(ot_totals.drop(labels=['Trip Count', 'Total Credit'],
                                        axis=1), horizontal=True)

            st.map()
