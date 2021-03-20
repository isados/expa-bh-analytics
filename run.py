#!/usr/bin/env python3

import os
import json
import requests
import urllib
import pygsheets
import numpy as np
import pandas as pd
from base64 import b64decode


if __name__ == "__main__":
    # Credentials from service account file for Google Sheets
    secretpath = "secret.json"
    with open(secretpath, 'wb') as f:
        f.write(b64decode(os.environ['GOOGLE_CREDS']))

    gc = pygsheets.authorize(service_file=secretpath)

    URI = 'https://gis-api.aiesec.org/graphql'
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

    # ORIGINAL_QUERY = '{allOpportunityApplication(filters: {created_at: {from:"2021-01-01", to:"2021-03-20"}}){data{id status created_at date_matched date_approved date_realized experience_start_date experience_end_date date_approval_broken nps_response_completed_at updated_at person{id full_name home_mc{id name}home_lc{id name}}host_lc{id name}home_mc{id name}opportunity{id created_at title available_openings duration sub_product{name}programme{id short_name_display}}standards{option}}}}'
    QUERY = '{allOpportunityApplication(filters: {created_at: {from:"2021-01-01", to:"2021-03-20"}}){data{id status created_at date_matched date_approved date_realized experience_start_date experience_end_date date_approval_broken nps_response_completed_at updated_at person{id full_name home_mc{name}home_lc{name}}host_lc{name}home_mc{name}opportunity{id created_at title duration sub_product{name}programme{short_name_display}}standards{option}}}}'

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
    results.replace([np.NaN], '-', inplace=True)

    results = json.loads(response.content)

    # Reduce the dict by 3
    results = results['data']['allOpportunityApplication']['data']

    #  Flatten dictionary and compress keys
    results = pd.json_normalize(results, sep='_')
    results.replace([np.NaN], '-', inplace=True)

    SPREADSHEET_ID = "1MQOyYpuJ4zF5xyqjVtAnrTrG3In9lxWl9L3yXiTeYiw"
    SHEET_NAME = "HEROKU"

    workbook = gc.open_by_key(SPREADSHEET_ID)
    worksheet = workbook.worksheet_by_title(SHEET_NAME)

    worksheet.set_dataframe(results, start='A1', copy_head=True)
