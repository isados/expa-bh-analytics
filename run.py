#!/usr/bin/env python3

import os
import tempfile
import pygsheets
import pandas as pd
import asyncio
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from utilities import write_base64str_obj_to_file


def main():
    # Select your transport with a defined url endpoint
    access_token = os.environ['ACCESS_TOKEN']
    transport = AIOHTTPTransport(url=f"https://gis-api.aiesec.org/graphql/?access_token={access_token}")

    async def getData():
        # Create a GraphQL client using the defined transport
        async with Client(transport=transport, fetch_schema_from_transport=True) as session:

            # Provide a GraphQL query
            query = gql(
                """
                query getApplicationList ($limit: Int, $start_date: DateTime, $end_date: DateTime){
                allOpportunityApplication(per_page: $limit, filters: {created_at: {from: $start_date, to: $end_date}}) {
                    data {
                    id
                    status
                    created_at
                    date_matched
                    date_pay_by_cash
                    date_approved
                    date_realized
                    experience_start_date
                    experience_end_date
                    date_approval_broken
                    nps_response_completed_at
                    updated_at
                    person {
                        id
                        full_name
                        home_mc {
                        name
                        }
                        home_lc {
                        name
                        }
                    }
                    host_lc {
                        name
                    }
                    host_mc: home_mc {
                        name
                    }
                    opportunity {
                        id
                        created_at
                        title
                        duration
                        sub_product {
                        name
                        }
                        programme {
                        short_name_display
                        }
                    }
                    standards {
                        option
                    }
                    }
                }
                }
            """
            )

            params = {	"mc_id": [518], # Bahrain's MC ID
                        "start_date": "2021-01-01",
                        "end_date": "",
                        "limit": 1000 # Could be any large enough number
                    }

            # Execute the query on the transport
            results = await session.execute(query, variable_values=params)
            # print(result)
            return results

    print("Executing query off of EXPA ...")
    results = asyncio.run(getData()) 


    print("Started preprocessing...")
    # Reduce the dict by 3 Levels
    results = results['allOpportunityApplication']['data']

    #  Flatten dictionary and compress keys
    results = pd.json_normalize(results, sep='_')

    # Create new columns for Easy Reading and Indices
    # * LC
    # * LC_ID
    # * Department
    # * Partner_MC
    # * Partner_LC

    # Create new multi-indices for grouping
    new_cols = ['dept_prefix', 'lc', 'partner_mc', 'partner_lc']

    def generate_new_fields(row):

        if row['person_home_mc_name'] == 'Bahrain':
            values = ['o', row['person_home_lc_name'],
                    row['host_mc_name'], row['host_lc_name']]
        else:
            values = ['i', row['host_lc_name'],
                    row['person_home_mc_name'], row['person_home_lc_name']]

        return dict(zip(new_cols, values))

    print("Generating new fields and tables ...")
    results[new_cols] = results.apply(lambda row: generate_new_fields(row), axis=1, result_type='expand')

    # Create a new field 'department' with incoming and outgoing labels as prefix
    results['department'] = results.dept_prefix + results.opportunity_programme_short_name_display
    results.drop('opportunity_programme_short_name_display', inplace=True, axis=1)
    results['department']

    """
    Produce Performance Analytics DataFrame
        * First convert dates from longform to YYYY-MM-DD
        * Group by Date, LC, Dept, PartnerMC, PartnerLC, and the metrics like # of Applications, Accepted etc.. will be the aggregation
    """

    date_cols = ['created_at', 'date_matched', 'date_approved', 'date_realized', 'updated_at']
    multi_indices = ['lc', 'department', 'partner_mc', 'partner_lc']
    counting_by = ['id', 'person_id']

    # Generate table with these columns only
    perf_table = results[counting_by + date_cols + multi_indices].copy()

    # Ensure that dates are uniform and shortened
    perf_table.loc[:,date_cols] = results[date_cols].applymap(lambda x: x[:-10], na_action='ignore')

    def splitup_date_field(table: pd.DataFrame, remaining_fields: list, sel_date_col: str, metric_name: str):
        table = table[[sel_date_col, *remaining_fields, *counting_by]]
        _ = table.sort_values([sel_date_col, *remaining_fields])
        _.rename(columns={sel_date_col: "date", 
                        "id": metric_name+"~APP", 
                        "person_id": metric_name+"~PPL"}, inplace=True)
        
        
        return _.dropna(axis=0)

    apps = splitup_date_field(perf_table, multi_indices, "created_at", "applications")
    acc = splitup_date_field(perf_table, multi_indices, "date_matched", "accepted")

    perf_analysis_df = pd.concat([apps, acc])

    # ### Push it to Google Sheets

    # Credentials from service account file for Google Sheets
    print("Creating temporary file for service account credentials...")

    temp = tempfile.NamedTemporaryFile()
    try:
        access_creds = os.environ['GOOGLE_CREDS']
        write_base64str_obj_to_file(access_creds, temp.name)
    finally:
        gc = pygsheets.authorize(service_file=temp.name)
        temp.close()

    print("Uploading to Google Sheets...")
    workbook = gc.open_by_key(os.environ["SPREADSHEET_ID"])
    perf_worksheet = workbook.worksheet_by_title(os.environ["SHEET_NAME"])

    perf_worksheet.set_dataframe(perf_analysis_df, start='A1', copy_head=True)
    print("Done!")

if __name__ == "__main__":
    main()
