#!/bin/bash

export ACCESS_TOKEN=$(cat creds/access_token)

# Service Account Credentials are stored in `base64encoded_creds` file
export GOOGLE_CREDS=$(cat creds/base64encoded_creds)

export SPREADSHEET_ID=1MQOyYpuJ4zF5xyqjVtAnrTrG3In9lxWl9L3yXiTeYiw
export SHEET_NAME=HEROKU
export START_DATE=2021-01-01
export END_DATE=
python3 run.py