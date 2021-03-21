#!/bin/bash

export ACCESS_TOKEN=7789a122c78d710a724f3cd2a7d8daf809b467d46cf63eafa76b2ae87a32f035

# Service Account Credentials are stored in `base64encoded_creds` file
export GOOGLE_CREDS=$(cat base64encoded_creds)

export SPREADSHEET_ID=1MQOyYpuJ4zF5xyqjVtAnrTrG3In9lxWl9L3yXiTeYiw
export SHEET_NAME=HEROKU
export START_DATE=2021-01-01
export END_DATE=
python3 run.py