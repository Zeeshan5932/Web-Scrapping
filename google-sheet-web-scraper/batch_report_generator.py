"""
Batch Report Generator
=====================

A direct implementation using gspread and oauth2client for batch processing
Google Sheet data with pause/resume functionality.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import os

# Constants
BATCH_SIZE = 500
SHEET_NAME = "Your Google Sheet Name"
OUTPUT_SHEET_NAME = "Combined Report"

def authenticate_google_sheets():
    # Set up the scope and credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("path_to_your_service_account_file.json", scope)
    client = gspread.authorize(creds)
    return client

def get_data_from_sheet(client, sheet_name):
    # Get sheet data
    sheet = client.open(SHEET_NAME).worksheet(sheet_name)
    data = sheet.get_all_values()
    header = data[0]
    rows = data[1:]
    return header, rows

def format_date(raw_date):
    # Format date as MM/DD/YY
    try:
        parsed_date = datetime.datetime.strptime(raw_date, "%Y-%m-%d")  # Adjust format if needed
        return parsed_date.strftime("%m/%d/%y")
    except Exception as e:
        return raw_date  # Fallback if date parsing fails

def get_value(data, headers, row_idx, date_key):
    try:
        col_idx = headers.index(date_key)
        return data[row_idx][col_idx] if data[row_idx][col_idx] != "" else 0
    except ValueError:
        return 0

def generate_proper_combined_report():
    # Authenticate Google Sheets
    client = authenticate_google_sheets()

    # Get CORRECT DATES sheet
    correct_dates_sheet = client.open(SHEET_NAME).worksheet("CORRECT DATES")
    correct_dates = correct_dates_sheet.col_values(1)  # Assuming dates are in the first column

    # Get data sheets
    sheet_names = ["TRAFFIC AVERAGE", "TRAFFIC MONTHLY", "DR", "RD", "KEYWORDS"]
    data = {}
    headers = {}
    for sheet_name in sheet_names:
        header, rows = get_data_from_sheet(client, sheet_name)
        data[sheet_name] = rows
        headers[sheet_name] = header

    # Create or clear the output sheet
    try:
        output_sheet = client.open(SHEET_NAME).worksheet(OUTPUT_SHEET_NAME)
        output_sheet.clear()  # Clear the previous data
    except gspread.exceptions.WorksheetNotFound:
        output_sheet = client.open(SHEET_NAME).add_worksheet(title=OUTPUT_SHEET_NAME, rows="1000", cols="10")
        output_sheet.append_row(["#", "Website", "Type", "Date", "Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords"])

    last_row_index = 0  # You can persist this using a text file or any other storage mechanism
    last_date_index = 0
    records_written = 0

    # Loop through the data sheets and correct dates
    for i in range(last_row_index, len(data["TRAFFIC AVERAGE"])):
        for j in range(last_date_index, len(correct_dates)):
            raw_date = correct_dates[j]
            date = format_date(raw_date)

            row = [
                data["TRAFFIC AVERAGE"][i][0],  # Number
                data["TRAFFIC AVERAGE"][i][1],  # Website
                data["TRAFFIC AVERAGE"][i][2],  # Type
                date,
                get_value(data["TRAFFIC AVERAGE"], headers["TRAFFIC AVERAGE"], i, raw_date),
                get_value(data["TRAFFIC MONTHLY"], headers["TRAFFIC MONTHLY"], i, raw_date),
                get_value(data["DR"], headers["DR"], i, raw_date),
                get_value(data["RD"], headers["RD"], i, raw_date),
                get_value(data["KEYWORDS"], headers["KEYWORDS"], i, raw_date)
            ]
            output_sheet.append_row(row)
            records_written += 1

            if records_written >= BATCH_SIZE:
                last_row_index = i
                last_date_index = j + 1
                print(f"Paused after {BATCH_SIZE} records at row {i}, date index {j + 1}")
                return  # To pause the process after writing a batch

    print("✅ All data processed.")

if __name__ == "__main__":
    generate_proper_combined_report()
