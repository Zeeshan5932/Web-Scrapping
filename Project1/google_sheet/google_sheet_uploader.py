from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import logging

def upload_to_google_sheets(notices, sheet_name="Scrapping"):
    try:
        # Define the scope for Google Sheets and Drive API
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Set the path to the credentials file
        creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'credentials.json')
        creds_path = os.path.abspath(creds_path)

        # Authorize the client using the credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        # Open the Google Sheet by name
        sheet = client.open(sheet_name).sheet1

        # Clear existing data in the sheet
        sheet.clear()

        # Add headers to the sheet
        headers = [
            "Publication Name", "Notice Date", "Full Text of Notice", "Location Name",
            "Street Address", "City", "State", "Zip Code", "Auction Sites", "Count of Tenants"
        ]
        sheet.append_row(headers)

        # Add each notice as a row in the sheet
        for notice in notices:
            row = [
                notice.get("Publication Name", "N/A"),
                notice.get("Notice Date", "N/A"),
                notice.get("Full Text of Notice", "N/A"),
                notice.get("Location Name", "N/A"),
                notice.get("Street Address", "N/A"),
                notice.get("City", "N/A"),
                notice.get("State", "N/A"),
                notice.get("Zip Code", "N/A"),
                ", ".join(notice.get("Auction Sites", [])),  # Convert list to comma-separated string
                notice.get("Count of Tenants", "N/A")
            ]
            sheet.append_row(row)

        logging.info(f"Successfully uploaded {len(notices)} notices to Google Sheets.")
    except Exception as e:
        logging.error(f"Error uploading to Google Sheets: {e}")
