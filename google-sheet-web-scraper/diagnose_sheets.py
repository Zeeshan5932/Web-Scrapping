"""
Diagnostic script to check actual sheet names in your Google Sheet
"""

import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_CONFIG

def check_actual_sheet_names():
    """Check what sheet names actually exist in your Google Sheet"""
    print("Checking actual sheet names in your Google Sheet...")
    print("=" * 60)
    
    try:
        # Authenticate
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEET_CONFIG['credentials_path'], scopes=scope
        )
        
        client = gspread.authorize(creds)
        
        # Open spreadsheet
        spreadsheet = client.open_by_url(GOOGLE_SHEET_CONFIG['sheet_url'])
        
        print(f"📋 Spreadsheet: {spreadsheet.title}")
        print()
        
        # Get all worksheets
        worksheets = spreadsheet.worksheets()
        
        print(f"📊 Found {len(worksheets)} sheets:")
        print()
        
        for i, worksheet in enumerate(worksheets, 1):
            row_count = worksheet.row_count
            col_count = worksheet.col_count
            print(f"   {i:2d}. \"{worksheet.title}\" ({row_count} rows × {col_count} cols)")
        
        print()
        print("🔍 Required sheet names (what the code expects):")
        required_sheets = ["Traffic Average", "Traffic Monthly", "DR", "RD", "Keywords", "CORRECT DATES"]
        
        for sheet_name in required_sheets:
            found = any(ws.title == sheet_name for ws in worksheets)
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"   - \"{sheet_name}\" ... {status}")
        
        print()
        print("💡 Sheet name comparison:")
        actual_names = [ws.title for ws in worksheets]
        
        for required in required_sheets:
            matches = [name for name in actual_names if name.upper() == required.upper()]
            if matches and matches[0] != required:
                print(f"   🔄 Expected: \"{required}\"")
                print(f"      Actual:   \"{matches[0]}\"")
                print(f"      → Need to rename!")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Check:")
        print("1. Credentials file exists and is valid")
        print("2. Google Sheet URL is correct")
        print("3. Service account has access to the sheet")

if __name__ == "__main__":
    check_actual_sheet_names()
