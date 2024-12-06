# Python Standard Library imports
import re
from datetime import datetime

### CONSTANTS ###

BASES_W_FLEETS = {
    'EWR':   ('320', '737', '756', '777', '787'),
    'DCA':   ('320', '737', '756', '777', '787'),
    'MCO':   ('737', ),
    'CLE':   ('737', ),
    'ORD':   ('320', '737', '756', '787'),
    'IAH':   ('320', '737', '756', '777', '787'),
    'DEN':   ('320', '737', '756', '787'),
    'LAS':   ('737', ),
    'LAX':   ('320', '737', '756', '787'),
    'SFO':   ('320', '737', '756', '777', '787'),
    'GUM':   ('737', )
}

SEATS = ('FO', 'CA')

ALL_CATS = [(b, e, s)
            for b in BASES_W_FLEETS for e in BASES_W_FLEETS[b] for s in SEATS]

BASES_FOR_OT = {
    'DEN': 'D',
    'EWR': 'E',
    'SFO': 'F',
    'GUM': 'G',
    'IAH': 'H',
    'LAS': 'J',
    'LAX': 'L',
    'MCO': 'M',
    'ORD': 'O',
    'CLE': 'V',
    'DCA': 'W'
}

EQUIP_FOR_OT = {
    '320': '1',
    '777': '2',
    '756': '3',
    '737': '5',
    '787': '8'
}

# List of bid months, each being a tuple of dates (from, to) inclusive in DDMMYY format. Should go into refdata and kept updated
BID_MONTHS = {
    # 2024/2025 Month Definitions
    'OCT2024': ('290924', '291024'),
    'NOV2024': ('301024', '291124'),
    'DEC2024': ('301124', '291224'),
    'JAN2025': ('301224', '290125'),
    'FEB2025': ('300125', '010325'),
    'MAR2025': ('020325', '310325'),
    'APR2025': ('010425', '300425')
    # 2025/2026 Month Definitions
    # todo
}

# List of bid months in datetime.date format, current month onwards


def str_to_date(d):
    return (datetime.strptime(d[0], '%d%m%y').date(), datetime.strptime(d[1], '%d%m%y').date())

BID_MONTHS_DT = {k: str_to_date(d) for k, d in BID_MONTHS.items()
                 if datetime.today().date() <= str_to_date(d)[1]} # Strip previous months

# This RE extracts the SKEY from a URL.
SKEY_RE = r'.+SKEY\=(?P<skey>.{41}).*'

# Payloads for HTML POST Requests

# Trading -> RSV Availability Display (UPA23)
FULL_RSV_URL_PAYLOAD = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': '/wEPDwUJNDkzOTg0MjM1ZGQHFu8g33TJYVIq7/Ufggrgq387Mg==',
    'ctl01$mHolder$txtDate': 'date',
    'BaseCombo1': 'the_base',
    'PositionCombo1': 'the_position',
    'EquipmentCombo1': 'the_equipment',
    'ctl01$mHolder$Submit': 'Submit',
    'ctl01$EID': '*EID*=UXXXXXX-->',
    'ctl01$Carrier': '*Carrier*=UA-->',
    'ctl01$Class': '*Class*=P-->',
    'ctl01$BidPeriodsHidden': '[&quot;2024-06-30&quot;,&quot;2024-07-01&quot;,&quot;2024-07-02&quot;,&quot;2024-07-03&quot;,&quot;2024-07-04&quot;,&quot;2024-07-05&quot;,&quot;2024-07-06&quot;,&quot;2024-07-07&quot;,&quot;2024-07-08&quot;,&quot;2024-07-09&quot;,&quot;2024-07-10&quot;,&quot;2024-07-11&quot;,&quot;2024-07-12&quot;,&quot;2024-07-13&quot;,&quot;2024-07-14&quot;,&quot;2024-07-15&quot;,&quot;2024-07-16&quot;,&quot;2024-07-17&quot;,&quot;2024-07-18&quot;,&quot;2024-07-19&quot;,&quot;2024-07-20&quot;,&quot;2024-07-21&quot;,&quot;2024-07-22&quot;,&quot;2024-07-23&quot;,&quot;2024-07-24&quot;,&quot;2024-07-25&quot;,&quot;2024-07-26&quot;,&quot;2024-07-27&quot;,&quot;2024-07-28&quot;,&quot;2024-07-29&quot;,&quot;2024-08-29&quot;,&quot;2024-08-30&quot;,&quot;2024-08-31&quot;,&quot;2024-09-01&quot;,&quot;2024-09-02&quot;,&quot;2024-09-03&quot;,&quot;2024-09-04&quot;,&quot;2024-09-05&quot;,&quot;2024-09-06&quot;,&quot;2024-09-07&quot;,&quot;2024-09-08&quot;,&quot;2024-09-09&quot;,&quot;2024-09-10&quot;,&quot;2024-09-11&quot;,&quot;2024-09-12&quot;,&quot;2024-09-13&quot;,&quot;2024-09-14&quot;,&quot;2024-09-15&quot;,&quot;2024-09-16&quot;,&quot;2024-09-17&quot;,&quot;2024-09-18&quot;,&quot;2024-09-19&quot;,&quot;2024-09-20&quot;,&quot;2024-09-21&quot;,&quot;2024-09-22&quot;,&quot;2024-09-23&quot;,&quot;2024-09-24&quot;,&quot;2024-09-25&quot;,&quot;2024-09-26&quot;,&quot;2024-09-27&quot;,&quot;2024-09-28&quot;,&quot;2024-10-30&quot;,&quot;2024-10-31&quot;,&quot;2024-11-01&quot;,&quot;2024-11-02&quot;,&quot;2024-11-03&quot;,&quot;2024-11-04&quot;,&quot;2024-11-05&quot;,&quot;2024-11-06&quot;,&quot;2024-11-07&quot;,&quot;2024-11-08&quot;,&quot;2024-11-09&quot;,&quot;2024-11-10&quot;,&quot;2024-11-11&quot;,&quot;2024-11-12&quot;,&quot;2024-11-13&quot;,&quot;2024-11-14&quot;,&quot;2024-11-15&quot;,&quot;2024-11-16&quot;,&quot;2024-11-17&quot;,&quot;2024-11-18&quot;,&quot;2024-11-19&quot;,&quot;2024-11-20&quot;,&quot;2024-11-21&quot;,&quot;2024-11-22&quot;,&quot;2024-11-23&quot;,&quot;2024-11-24&quot;,&quot;2024-11-25&quot;,&quot;2024-11-26&quot;,&quot;2024-11-27&quot;,&quot;2024-11-28&quot;,&quot;2024-11-29&quot;]',
    '__VIEWSTATEGENERATOR': 'A4FAF84E'
}

# Trading -> Open Time
FULL_OT_URL_PAYLOAD = {
    '__VIEWSTATE': '/wEPDwUJNTU4NzU2MjAzDxYCHhNWYWxpZGF0ZVJlcXVlc3RNb2RlAgEWAmYPZBYEAgEPZBYEAgoPFgIeBGhyZWYFIH4vQ29udGVudC9hcHAvaWNvbnMvSWNvbi01MTIucG5nZAIcDxYCHgRUZXh0Be0CPHNjcmlwdCBzcmM9Ii9DQ1MvanMvanF1ZXJ5LTMuNS4xLm1pbi5qcyIgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij48L3NjcmlwdD48c2NyaXB0IHNyYz0iL0NDUy9TY3JpcHRzL2pxdWVyeS11aS5taW4uanMiIHR5cGU9InRleHQvamF2YXNjcmlwdCI+PC9zY3JpcHQ+PHNjcmlwdCBzcmM9Ii9DQ1MvU2NyaXB0cy9qcXVlcnkudmFsaWRhdGUubWluLmpzIiB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPjwvc2NyaXB0PjxzY3JpcHQgc3JjPSIvQ0NTL2pzL3BsdWdpbnMvcHVybC5qcyIgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij48L3NjcmlwdD48c2NyaXB0IHNyYz0iL0NDUy9qcy9VdGlscy5qcyIgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij48L3NjcmlwdD5kAgMPZBYKAgMPZBYGAgEPFgIfAQU6fi9NYWluLmFzcHg/U0tFWT0wMzIwYjFlY2E4NDYxMmM0OTEyOTE1ZGFlOWQxYTQ2NmM2YjIzNjQ0NGQCBQ8WAh4JaW5uZXJodG1sZWQCCQ8WAh8DBQ1UcmlwIFNob3BwaW5nZAIFD2QWBgIDDxYCHwEFOn4vTWFpbi5hc3B4P1NLRVk9MDMyMGIxZWNhODQ2MTJjNDkxMjkxNWRhZTlkMWE0NjZjNmIyMzY0NDRkAgUPFgIfAwUWSk9OQVRIQU4gSCBPVUdIT1VSTElBTmQCBw8WAh8DBQ1UcmlwIFNob3BwaW5nZAIJD2QWAmYPZBYCAgEPDxYCHwJlZGQCCw9kFgQCAQ8WAh8BBUkvQ0NTL0xvZ29mZjIuYXNweD9TS0VZPTAzMjBiMWVjYTg0NjEyYzQ5MTI5MTVkYWU5ZDFhNDY2YzZiMjM2NDQ0JkxvZ29mZj0xZAIDDxYCHwEFQS9DQ1MvTWVudXBhZ2UuYXNweD9TS0VZPTAzMjBiMWVjYTg0NjEyYzQ5MTI5MTVkYWU5ZDFhNDY2YzZiMjM2NDQ0ZAIPDxYCHwMFP0NvcHlyaWdodCAmY29weTsgMjAyNCBVbml0ZWQgQWlybGluZXMsIEluYy4gQWxsIFJpZ2h0cyBSZXNlcnZlZGRkZWBxXNmS3fcArMABc7WGYuFl9MM=',
    'SearchCriteriaStatus': 'show',
    'txtStartDate': '',  # start date
    'svStartDate': '',
    'txtEndDate': '',  # end date
    'svEndDate': '',
    'txtPairDaysMin': '',
    'svPairDaysMin': '',
    'txtPairDaysMax': '',
    'svPairDaysMax': '',
    'selBase': '',  # base single letter, use BASES_FOR_OT
    'svBase': '',
    'selEquip': '',
    'svEquip': '',
    'selPos': '',
    'svPos': '',
    'selResv': 'N',  # no reserves
    'svResv': 'Y',
    'svShowAds': 'false',
    'svShowAdsMutual': 'false',
    'chkShowOpen': 'on',  # show open time
    'svShowOpen': 'true',
    'svShowTrain': 'false',
    'selSort': '1',
    'svSort': '1',
    'svSortDesc': 'false',
    'selSort2': '3',
    'svSort2': '3',
    'svSortDesc2': 'false',
    'SearchDetailsStatus': 'hide',
    'TestDetailsStatus': 'hide',
    'txtPairingNumber': '',
    'svPairingNumber': '',
    'txtBlockTimeMin': '',
    'svBlockTimeMin': '',
    'txtBlockTimeMax': '',
    'svBlockTimeMax': '',
    'txtReportTimeMin': '',
    'svReportTimeMin': '',
    'txtReportTimeMax': '',
    'svReportTimeMax': '',
    'txtEndingTimeMin': '',
    'svEndingTimeMin': '',
    'txtEndingTimeMax': '',
    'svEndingTimeMax': '',
    'txtNumPerPage': '15',  # number per page max 99
    'svNumPerPage': '15',
    'chkBrief': 'on',  # single page on
    'svBrief': 'true',
    'Submitter': 'Display Pairings',
    'EOTQID': '56082',
    'SOTQID': '0',
    'LastPage': '0',
    'From': 'OT',
    'AdvertiseCount': '0',
    'OtherChkboxCount': '0',
    'MutualTradeCount': '0',
    'CartSelectCount': '0',
    'QuerySelectCount': '0',
    'Resort': '0',
    'Page4.x': '6',  # ????????
    'Page4.y': '11',  # ?????????
    'ctl01$EID': '*EID*=UXXXXXX-->',
    'ctl01$Carrier': '*Carrier*=UA-->',
    'ctl01$Class': '*Class*=P-->',
    'ctl01$BidPeriodsHidden': '[&quot;2024-07-30&quot;,&quot;2024-07-31&quot;,&quot;2024-08-01&quot;,&quot;2024-08-02&quot;,&quot;2024-08-03&quot;,&quot;2024-08-04&quot;,&quot;2024-08-05&quot;,&quot;2024-08-06&quot;,&quot;2024-08-07&quot;,&quot;2024-08-08&quot;,&quot;2024-08-09&quot;,&quot;2024-08-10&quot;,&quot;2024-08-11&quot;,&quot;2024-08-12&quot;,&quot;2024-08-13&quot;,&quot;2024-08-14&quot;,&quot;2024-08-15&quot;,&quot;2024-08-16&quot;,&quot;2024-08-17&quot;,&quot;2024-08-18&quot;,&quot;2024-08-19&quot;,&quot;2024-08-20&quot;,&quot;2024-08-21&quot;,&quot;2024-08-22&quot;,&quot;2024-08-23&quot;,&quot;2024-08-24&quot;,&quot;2024-08-25&quot;,&quot;2024-08-26&quot;,&quot;2024-08-27&quot;,&quot;2024-08-28&quot;,&quot;2024-09-29&quot;,&quot;2024-09-30&quot;,&quot;2024-10-01&quot;,&quot;2024-10-02&quot;,&quot;2024-10-03&quot;,&quot;2024-10-04&quot;,&quot;2024-10-05&quot;,&quot;2024-10-06&quot;,&quot;2024-10-07&quot;,&quot;2024-10-08&quot;,&quot;2024-10-09&quot;,&quot;2024-10-10&quot;,&quot;2024-10-11&quot;,&quot;2024-10-12&quot;,&quot;2024-10-13&quot;,&quot;2024-10-14&quot;,&quot;2024-10-15&quot;,&quot;2024-10-16&quot;,&quot;2024-10-17&quot;,&quot;2024-10-18&quot;,&quot;2024-10-19&quot;,&quot;2024-10-20&quot;,&quot;2024-10-21&quot;,&quot;2024-10-22&quot;,&quot;2024-10-23&quot;,&quot;2024-10-24&quot;,&quot;2024-10-25&quot;,&quot;2024-10-26&quot;,&quot;2024-10-27&quot;,&quot;2024-10-28&quot;,&quot;2024-10-29&quot;,&quot;2024-11-30&quot;,&quot;2024-12-01&quot;,&quot;2024-12-02&quot;,&quot;2024-12-03&quot;,&quot;2024-12-04&quot;,&quot;2024-12-05&quot;,&quot;2024-12-06&quot;,&quot;2024-12-07&quot;,&quot;2024-12-08&quot;,&quot;2024-12-09&quot;,&quot;2024-12-10&quot;,&quot;2024-12-11&quot;,&quot;2024-12-12&quot;,&quot;2024-12-13&quot;,&quot;2024-12-14&quot;,&quot;2024-12-15&quot;,&quot;2024-12-16&quot;,&quot;2024-12-17&quot;,&quot;2024-12-18&quot;,&quot;2024-12-19&quot;,&quot;2024-12-20&quot;,&quot;2024-12-21&quot;,&quot;2024-12-22&quot;,&quot;2024-12-23&quot;,&quot;2024-12-24&quot;,&quot;2024-12-25&quot;,&quot;2024-12-26&quot;,&quot;2024-12-27&quot;,&quot;2024-12-28&quot;,&quot;2024-12-29&quot;]',
    '__VIEWSTATEGENERATOR': 'AA2A2EBD'
}

# Flight Planning -> Pairing Info
FULL_PI_URL_PAYLOAD = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': '/wEPDwULLTE5NDMyNjkxMzZkZDHMkRzQ9gHo9ddmcB7CEDYJ5ZgO',
    'ctl01$mHolder$txtPairingNumber': '',  # this is where the pairing number goes
    'ctl01$mHolder$txtDate': '',  # pairing date
    # S = as scheduled which includes pay info, #A = actual
    'ctl01$mHolder$ddlActSched': 'S',
    'ctl01$mHolder$ddlClass': 'P',
    'ctl01$mHolder$cmdSubmit': 'Submit',
    'ctl01$EID': '*EID*=UXXXXXX-->',
    'ctl01$Carrier': '*Carrier*=UA-->',
    'ctl01$Class': '*Class*=P-->',
    'ctl01$BidPeriodsHidden': '[&quot;2024-07-30&quot;,&quot;2024-07-31&quot;,&quot;2024-08-01&quot;,&quot;2024-08-02&quot;,&quot;2024-08-03&quot;,&quot;2024-08-04&quot;,&quot;2024-08-05&quot;,&quot;2024-08-06&quot;,&quot;2024-08-07&quot;,&quot;2024-08-08&quot;,&quot;2024-08-09&quot;,&quot;2024-08-10&quot;,&quot;2024-08-11&quot;,&quot;2024-08-12&quot;,&quot;2024-08-13&quot;,&quot;2024-08-14&quot;,&quot;2024-08-15&quot;,&quot;2024-08-16&quot;,&quot;2024-08-17&quot;,&quot;2024-08-18&quot;,&quot;2024-08-19&quot;,&quot;2024-08-20&quot;,&quot;2024-08-21&quot;,&quot;2024-08-22&quot;,&quot;2024-08-23&quot;,&quot;2024-08-24&quot;,&quot;2024-08-25&quot;,&quot;2024-08-26&quot;,&quot;2024-08-27&quot;,&quot;2024-08-28&quot;,&quot;2024-09-29&quot;,&quot;2024-09-30&quot;,&quot;2024-10-01&quot;,&quot;2024-10-02&quot;,&quot;2024-10-03&quot;,&quot;2024-10-04&quot;,&quot;2024-10-05&quot;,&quot;2024-10-06&quot;,&quot;2024-10-07&quot;,&quot;2024-10-08&quot;,&quot;2024-10-09&quot;,&quot;2024-10-10&quot;,&quot;2024-10-11&quot;,&quot;2024-10-12&quot;,&quot;2024-10-13&quot;,&quot;2024-10-14&quot;,&quot;2024-10-15&quot;,&quot;2024-10-16&quot;,&quot;2024-10-17&quot;,&quot;2024-10-18&quot;,&quot;2024-10-19&quot;,&quot;2024-10-20&quot;,&quot;2024-10-21&quot;,&quot;2024-10-22&quot;,&quot;2024-10-23&quot;,&quot;2024-10-24&quot;,&quot;2024-10-25&quot;,&quot;2024-10-26&quot;,&quot;2024-10-27&quot;,&quot;2024-10-28&quot;,&quot;2024-10-29&quot;,&quot;2024-11-30&quot;,&quot;2024-12-01&quot;,&quot;2024-12-02&quot;,&quot;2024-12-03&quot;,&quot;2024-12-04&quot;,&quot;2024-12-05&quot;,&quot;2024-12-06&quot;,&quot;2024-12-07&quot;,&quot;2024-12-08&quot;,&quot;2024-12-09&quot;,&quot;2024-12-10&quot;,&quot;2024-12-11&quot;,&quot;2024-12-12&quot;,&quot;2024-12-13&quot;,&quot;2024-12-14&quot;,&quot;2024-12-15&quot;,&quot;2024-12-16&quot;,&quot;2024-12-17&quot;,&quot;2024-12-18&quot;,&quot;2024-12-19&quot;,&quot;2024-12-20&quot;,&quot;2024-12-21&quot;,&quot;2024-12-22&quot;,&quot;2024-12-23&quot;,&quot;2024-12-24&quot;,&quot;2024-12-25&quot;,&quot;2024-12-26&quot;,&quot;2024-12-27&quot;,&quot;2024-12-28&quot;,&quot;2024-12-29&quot;]',
    '__VIEWSTATEGENERATOR': '2843D6C1',
}

### HELPER FUNCTIONS ###


def date_to_bidmonth(d):
    # Returns the bid month associated with a datetime.date
    for bid_month, bid_month_dates in BID_MONTHS_DT.items():
        if (d >= bid_month_dates[0]) and (d <= bid_month_dates[1]):
            return bid_month
    return None


def skey_from_user():
    """Prompts user to input CCS URL and extracts the SKEY

    Raises:
        ValueError: No SKEY in URL

    Returns:
       String: SKEY
    """
    ccs_url = input("Login to CCS and copy-paste URL here: ")
    if match := re.match(SKEY_RE, ccs_url):
        skey = match.group('skey')
    else:
        raise ValueError(f'No valid SKEY found in the URL!')

    return skey
