#!/usr/bin/env python3

import os
import json
import tempfile
import requests
import urllib
import pygsheets
import numpy as np
import pandas as pd
from string import Template
from utilities import write_base64str_obj_to_file


class InvalidStartDate(Exception):
    """Raised when the Start Date isn't valid or missing"""
    pass


if __name__ == "__main__":
    # Credentials from service account file for Google Sheets

    print("Creating temporary file for service account credentials...")

    temp = tempfile.NamedTemporaryFile()
    try:
        write_base64str_obj_to_file(os.environ['GOOGLE_CREDS'], temp.name)
    finally:
        gc = pygsheets.authorize(service_file=temp.name)
        temp.close() #5


    URI = 'https://gis-api.aiesec.org/graphql'
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

    START_DATE = os.environ['START_DATE']
    END_DATE = os.environ['END_DATE']

    if START_DATE in ["", None]:
        raise InvalidStartDate

    if END_DATE is None:
        END_DATE = ""

    QUERY = Template('{allOpportunityApplication(filters: {created_at: {from:"$start", to:"$end"}}){data{id status created_at date_matched date_approved date_realized experience_start_date experience_end_date date_approval_broken nps_response_completed_at updated_at person{id full_name home_mc{name}home_lc{name}}host_lc{name}home_mc{name}opportunity{id created_at title duration sub_product{name}programme{short_name_display}}standards{option}}}}')
    QUERY = QUERY.substitute(start=START_DATE, end=END_DATE)

    url = f"{URI}?query={QUERY}&access_token={ACCESS_TOKEN}"

    url = urllib.parse.quote(url, safe='~@#$&()*!+=:;,.?/\'')

    response = requests.post(url, data={'Content-Type': 'application/json'})
    print(response.status_code)
    if response.status_code != 200:
        print("Error Occured from Expa Endpoint")
        print(response)

    results = json.loads(response.content)

    # Reduce the dict by 3
    results = results['data']['allOpportunityApplication']['data']

    #  Flatten dictionary and compress keys
    results = pd.json_normalize(results, sep='_')
    results.replace([np.NaN], '', inplace=True)

    results = json.loads(response.content)

    # Reduce the dict by 3 Levels
    results = results['data']['allOpportunityApplication']['data']

    #  Flatten dictionary and compress keys
    results = pd.json_normalize(results, sep='_')
    results.replace([np.NaN, "", "-"], '', inplace=True)

    SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
    SHEET_NAME = os.environ["SHEET_NAME"]

    workbook = gc.open_by_key(SPREADSHEET_ID)
    worksheet = workbook.worksheet_by_title(SHEET_NAME)

    worksheet.set_dataframe(results, start='A1', copy_head=True)
