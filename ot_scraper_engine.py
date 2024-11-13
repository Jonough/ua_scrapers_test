# Python Standard Library imports
import argparse
import datetime
import io
import os
import random
import re
import time
from pathlib import Path
import requests
from datetime import timedelta

# Third Party Imports
import pandas as pd

# Local Imports
from ua_scrapers_ref import *

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
        'txtNumPerPage': '99',  # limited to 99 per page
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
    """Takes a session key, category, bid month and returns a list of open time
    """

    # Create the OT URL with the session key
    ot_url = (f'https://ccs.ual.com/CCS/opentime.aspx?'
              f'SKEY={skey}&CMS=False')
    
    # Shamelessly stolen from CCS Reserve Scraper
    max_attempts = 3
    attempts = 1
    raw_html = ''
    while attempts <= max_attempts:
        time.sleep(random.uniform(0.5, 4.5))
        raw_html = extract_ot_html(ot_url, cat, BID_MONTHS[bid_month])
        bad_html = 'error occurred' in raw_html
        if bad_html:
            attempts += 1
            if attempts >= max_attempts:
                return None  # Return an empty list
        else:
            # Used to be a warning here
            break

    ot_display_html = io.StringIO(initial_value=raw_html)
    all_tables = pd.read_html(ot_display_html)

    # Once the clipboard (myPairings) is clear on open time page (IMPORTANT), 10th table is the list of OT (9th index)
    ot = all_tables[9]

    # Cleanup
    ot.columns = ot.iloc[0]
    ot = ot.iloc[1:, 1:3]

    # Generate a warning if >= limit of 99 trips per page
    if (len(ot) == 99):
        # Used to be a warning here
        return None

    # Now to find the pay times - if the table includes 'Pay Time', then extract the pay and dhd times
    # For some unknown and annyoing reason, CCS Open Time 'Pay Time' doesn't include the deadhead time, so if there is DHD time we need to add it in
    pay_times = []
    for t in all_tables:
        if t.isin(['Pay Time']).any().any():
            # Pay Time at location 1,5 in Dataframe
            p = t.at[1, 5]
            # Deadhead time at location 1,2 in Dataframe
            d = t.at[1, 2]
            # If d not equal d, it means it's NaN i.e. No DHD pay
            if (d != d):
                # No deadhead pay, just add the colon and record the pay time
                pay_times.append(f'{p[:2]}:{p[2:]}')
            else:
                # Deadhead pay, now we have to do some work.. add both using timedelta
                p_td = timedelta(hours=int(p[:2]), minutes=int(p[2:]))
                d_td = timedelta(hours=int(d[:2]), minutes=int(d[2:]))
                total = td_hhmm(p_td + d_td)  # add and convert to hh:mm String
                pay_times.append(total)

    # Add pay times to the open time list
    ot['Pay Time'] = pay_times

    return ot

def ot_totals():
    pass
    #Dictionary of Base: (total credit hours, no of trips)

def initialize_session(skey):
    session = requests.Session()

    ot_url = (f'https://ccs.ual.com/CCS/opentime.aspx?'
              f'SKEY={skey}&CMS=False')
    
    if (session.get(ot_url, verify=False, headers=requests.utils.default_headers()).status_code != 200):
        raise ValueError(msg='Session is not valid!')