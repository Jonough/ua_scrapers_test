# Python Standard Library imports
import argparse
from datetime import datetime
from datetime import timedelta
import io
import os
import random
import re
import time
from pathlib import Path
import requests

# Third Party Imports
import pandas as pd

# Local Imports
from ua_scrapers_ref import *

# CONSTANTS

OT_DF_FORMAT = ['Pairing Number', 'Category',
                'Pairing Date', 'Pairing End Date', 'Days', 'Pay Time', 'Pay Minutes']

OT_DF_DTYPES = {
    'Pairing Number': str,
    'Category': str,
    'Pairing Date': str,
    'Pairing End Date': str,
    'Days': int,
    'Pay Time': str,
    'Pay Minutes': int
}

# HELPER FUNCTIONS


def mins_to_dur(mins):
    # Takes an int number of minutes and returns a duration string
    try:
        h = int(mins / 60)
        m = int(mins % 60)
    except:
        print('Error with minutes format: {mins}')
        return 'err'

    h = str(h)
    m = str(m)
    if len(m) == 1:
        # Single digit, append a 0
        m = f'0{m}'
    return (f'{h}:{m}')


def dur_to_mins(d):
    # Takes a time in hhh:mm format and returns the number of minutes
    # Returns -1 if there was an error
    total_mins = 0
    d = d.strip(',') # Remove commas
    try:
        s = str.split(d, sep=':')
        # Error checking for correct number after split (should be 2)
        if len(s) != 2:
            print(f'Error with duration format: {d}')
            return -1
        # Hours can be 1 or more digits, but mins has to be 2
        if len(s[1]) != 2:
            print(f'Error with duration format: {d}')
            return -1

        # These will throw an exception if they don't convert to int
        h = int(s[0])
        m = int(s[1])

        # Minutes should be 0 to 59
        if (m > 59):
            print(f'Error with minutes format: {m}')
            return -1
    except:
        print(f'Format error with {d}')
        return -1

    return m + (60*h)


def str_to_dur(s):
    # Takes a string s and returns it in hhh:mm format
    # Might want to add some validation here

    # Remove whitespaces
    s = s.strip()

    # Hours is everything but the last two digits
    h = s[:-2]

    # Minutes is the last two, strip everything else
    m = s[-2:]

    return f'{h}:{m}'

# MAIN FUNCTIONS


def extract_ot_html(ot_url, cat, bid_month):
    """
    Extracts and returns the raw html text of the relevant category and bid month from the CCS -> Trading -> Open Time page
    """
    ot_url_payload = {
        '__VIEWSTATE': '/wEPDwUJNTU4NzU2MjAzDxYCHhNWYWxpZGF0ZVJlcXVlc3RNb2RlAgEWAmYPZBYEAgEPZBYEAgoPFgIeBGhyZWYFIH4vQ29udGVudC9hcHAvaWNvbnMvSWNvbi01MTIucG5nZAIcDxYCHgRUZXh0Be0CPHNjcmlwdCBzcmM9Ii9DQ1MvanMvanF1ZXJ5LTMuNS4xLm1pbi5qcyIgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij48L3NjcmlwdD48c2NyaXB0IHNyYz0iL0NDUy9TY3JpcHRzL2pxdWVyeS11aS5taW4uanMiIHR5cGU9InRleHQvamF2YXNjcmlwdCI+PC9zY3JpcHQ+PHNjcmlwdCBzcmM9Ii9DQ1MvU2NyaXB0cy9qcXVlcnkudmFsaWRhdGUubWluLmpzIiB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPjwvc2NyaXB0PjxzY3JpcHQgc3JjPSIvQ0NTL2pzL3BsdWdpbnMvcHVybC5qcyIgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij48L3NjcmlwdD48c2NyaXB0IHNyYz0iL0NDUy9qcy9VdGlscy5qcyIgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij48L3NjcmlwdD5kAgMPZBYKAgMPZBYGAgEPFgIfAQU6fi9NYWluLmFzcHg/U0tFWT0wMzIwYjFlY2E4NDYxMmM0OTEyOTE1ZGFlOWQxYTQ2NmM2YjIzNjQ0NGQCBQ8WAh4JaW5uZXJodG1sZWQCCQ8WAh8DBQ1UcmlwIFNob3BwaW5nZAIFD2QWBgIDDxYCHwEFOn4vTWFpbi5hc3B4P1NLRVk9MDMyMGIxZWNhODQ2MTJjNDkxMjkxNWRhZTlkMWE0NjZjNmIyMzY0NDRkAgUPFgIfAwUWSk9OQVRIQU4gSCBPVUdIT1VSTElBTmQCBw8WAh8DBQ1UcmlwIFNob3BwaW5nZAIJD2QWAmYPZBYCAgEPDxYCHwJlZGQCCw9kFgQCAQ8WAh8BBUkvQ0NTL0xvZ29mZjIuYXNweD9TS0VZPTAzMjBiMWVjYTg0NjEyYzQ5MTI5MTVkYWU5ZDFhNDY2YzZiMjM2NDQ0JkxvZ29mZj0xZAIDDxYCHwEFQS9DQ1MvTWVudXBhZ2UuYXNweD9TS0VZPTAzMjBiMWVjYTg0NjEyYzQ5MTI5MTVkYWU5ZDFhNDY2YzZiMjM2NDQ0ZAIPDxYCHwMFP0NvcHlyaWdodCAmY29weTsgMjAyNCBVbml0ZWQgQWlybGluZXMsIEluYy4gQWxsIFJpZ2h0cyBSZXNlcnZlZGRkZWBxXNmS3fcArMABc7WGYuFl9MM=',
        'SearchCriteriaStatus': 'show',
        'txtStartDate': bid_month[0],  # start date
        'txtEndDate': bid_month[1],  # end date
        # base single letter, use BASES_FOR_OT[base]
        'selBase': BASES_FOR_OT[cat[0]],
        # numbered, use EQUIP_FOR_OT[equipment]
        'selEquip': EQUIP_FOR_OT[cat[1]],
        'selPos': cat[2],
        'selResv': 'N',  # no reserves
        'chkShowOpen': 'on',  # show open time
        'selSort': '1',
        'selSort2': '3',
        # 'chkBrief' : 'on', #single page - turned off to maintain pay time information
        'txtNumPerPage': '499',  # limited to 499 per page
        'Submitter': 'Display Pairings',
        'From': 'OT',
        'AdvertiseCount': '0',
        'OtherChkboxCount': '0',
        'MutualTradeCount': '0',
        'CartSelectCount': '0',
        'QuerySelectCount': '0',
        'Resort': '0',
        '__VIEWSTATEGENERATOR': 'AA2A2EBD'
    }

    ot_html = requests.post(url=ot_url, data=ot_url_payload,
                            headers=requests.utils.default_headers()).text
    return ot_html


def extract_ot_list(skey, cat, bid_month):
    """Takes a session key, category, bid month and returns a dataframe of open time
    """

    # Create the OT URL with the session key
    ot_url = (f'https://ccs.ual.com/CCS/opentime.aspx?'
              f'SKEY={skey}&CMS=False')

    # Shamelessly stolen from CCS Reserve Scraper
    max_attempts = 3
    attempts = 1
    raw_html = ''
    while attempts <= max_attempts:
        time.sleep(random.uniform(2, 4.5))
        raw_html = extract_ot_html(ot_url, cat, BID_MONTHS[bid_month])
        bad_html = 'error occurred' in raw_html
        if bad_html:
            attempts += 1
            if attempts >= max_attempts:
                return pd.DataFrame() # Return empty dataframe
        else:
            # Used to be a warning here
            break

    ot_display_html = io.StringIO(initial_value=raw_html)
    all_tables = pd.read_html(ot_display_html)

    # Once the clipboard (myPairings) is clear on open time page (IMPORTANT), 10th table is the list of OT (9th index)
    ot = all_tables[9]

    # Cleanup
    try:
        ot.columns = ot.iloc[0]
        ot = ot.iloc[1:]
        ot = ot[['Pairing Number', 'Pairing Date', 'Days']]
    except:
        # Issue parsing, possibly empty list or grabbed the wrong table
        return pd.DataFrame()

    # Add Category column
    ot['Category'] = str(cat[0]) + str(cat[1]) + str(cat[2])

    # Generate a warning if >= limit of 99 trips per page
    #if (len(ot) == 99):
        # Used to be a warning here
    #    return pd.DataFrame() # Return empty dataframe

    # Now to find the pay times - if the table includes 'Pay Time', then extract the pay and dhd times
    # For some unknown and annyoing reason, CCS Open Time 'Pay Time' doesn't include the deadhead time, so if there is DHD time we need to add it in
    pay_times = []
    pay_minutes = []
    for t in all_tables:
        if t.isin(['Pay Time']).any().any():
            # Pay Time at location 1,5 in Dataframe
            p = t.at[1, 5]
            # Deadhead time at location 1,2 in Dataframe
            d = t.at[1, 2]
            # If d not equal d, it means it's NaN i.e. No DHD pay
            if (d != d):
                p = str(p) # convert to string
                # No DHD pay, just take the pay time, convert it to a duration string then minutes
                p_duration = str_to_dur(p)  # CCS format to duration
                p_minutes = dur_to_mins(p_duration)  # duration to minutes
                # minutes back to duration (our formatting with a colon)
                p_duration = mins_to_dur(p_minutes)

                # Save the results
                pay_minutes.append(p_minutes)
                pay_times.append(p_duration)
            else:
                p, d = str(p), str(d) # convert to string
                # Deadhead pay, now we have to add pay and dhd
                p_duration, d_duration = str_to_dur(
                    p), str_to_dur(d)  # CCS format to duration
                p_minutes, d_minutes = dur_to_mins(p_duration), dur_to_mins(
                    d_duration)  # duration to minutes
                total_pay = p_minutes + d_minutes  # Sum Pay + DHD
                # Convert it back to duration (our formatting)
                total_duration = mins_to_dur(total_pay)

                # Save the results
                pay_minutes.append(total_pay)
                pay_times.append(total_duration)

    # Add pay times to the open time list
    ot['Pay Time'] = pay_times
    ot['Pay Minutes'] = pay_minutes

    # Pairing Date string to datetime.date object
    ot['Pairing Date'] = ot.apply(lambda d: datetime.strptime(
        d['Pairing Date'], '%d%m%y').date(), axis=1)

    # Convert Days to int
    ot['Days'] = ot.apply(lambda d: int(d['Days']), axis=1)

    # Calculate pairing end date
    ot['Pairing End Date'] = ot.apply(
        lambda d: d['Pairing Date'] + timedelta(days=d['Days'] - 1), axis=1)

    if not ot.empty:
        # If we have data, reorder the columns
        ot_index = OT_DF_FORMAT
        ot = ot[ot_index]

    return ot


def calculate_ot_totals(ot):
    # Takes DataFrame of OT (with pay minutes) and returns a dataframe of totals per category
    # Resulting DataFrame format: Category | Trip Count | Total Credit | Pay Minutes
    if ot.empty:
        return pd.DataFrame()

    grouped = ot.groupby('Category')

    # Save results in a dictionary for now
    ot_totals = {}

    # Go through each category and sum pay times
    for cat, ot_list in grouped:
        total = ot_list['Pay Minutes'].sum()
        # Trip Count, Total Credit, Pay Minutes
        ot_totals[cat] = [len(ot_list), mins_to_dur(total), total]

    # Convert our dictionary to a dataframe
    df = pd.DataFrame.from_dict(ot_totals, orient='index',
                                columns=['Trip Count', 'Total Credit', 'Pay Minutes'])
    df.index.name = 'Category'

    return df


def initialize_session(skey):
    session = requests.Session()

    ot_url = (f'https://ccs.ual.com/CCS/opentime.aspx?'
              f'SKEY={skey}&CMS=False')

    if (session.get(ot_url, verify=False, headers=requests.utils.default_headers()).status_code != 200):
        raise ValueError(msg='Session is not valid!')
